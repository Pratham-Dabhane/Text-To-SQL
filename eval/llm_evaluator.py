"""Evaluate local LLM-generated SQL against the golden dataset."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from sqlalchemy.engine import Engine

from eval.evaluator import result_shape_matches, rows_match
from text_to_sql.alignment import judge_alignment
from text_to_sql.execution import execute_read_only
from text_to_sql.ollama_client import OllamaClient
from text_to_sql.generation import generate_validated_sql
from text_to_sql.schema import inspect_schema
from text_to_sql.schema_prompt import format_schema_for_prompt
from text_to_sql.sql_response import clean_generated_sql
from text_to_sql.sql_validation import validate_read_only_sql


def score_generated_sql(
    case: dict[str, Any], generated_sql: str,
    executor: Callable[[str], dict[str, Any]],
) -> bool:
    cleaned = clean_generated_sql(generated_sql)
    validated = validate_read_only_sql(cleaned)
    result = executor(validated)
    return rows_match(result["rows"], result["columns"], case["expected_rows"])


def evaluate_model(
    engine: Engine,
    dataset_path: str | Path,
    client: OllamaClient | None = None,
    include_alignment: bool = False,
) -> dict[str, Any]:
    cases = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    schema_text = format_schema_for_prompt(inspect_schema(engine))
    model_client = client or OllamaClient()
    results = []

    for case in cases:
        generated = None
        try:
            generated, validated = generate_validated_sql(
                case["question"], schema_text, model_client
            )
            output = execute_read_only(engine, validated)
            correct = rows_match(output["rows"], output["columns"], case["expected_rows"])
            result_record = {
                "id": case["id"],
                "correct": correct,
                "result_shape_ok": result_shape_matches(
                    output["columns"], case["expected_rows"]
                ),
                "generated_sql": generated,
                "validated_sql": validated,
            }
            if include_alignment:
                try:
                    result_record["alignment"] = judge_alignment(
                        case["question"], validated, model_client
                    )
                except Exception as alignment_error:
                    result_record["alignment_error"] = str(alignment_error)
            results.append(result_record)
        except Exception as exc:  # Record failures as incorrect, never hide them.
            results.append({
                "id": case["id"],
                "correct": False,
                "generated_sql": generated if "generated" in locals() else None,
                "error": str(exc),
            })

    correct_count = sum(result["correct"] for result in results)
    return {
        "total": len(results),
        "correct": correct_count,
        "execution_accuracy": correct_count / len(results) if results else 0.0,
        "results": results,
    }


def evaluate_repeated(
    engine: Engine,
    dataset_path: str | Path,
    *,
    runs: int = 3,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Run evaluation repeatedly to expose local-model variability."""
    if runs < 1:
        raise ValueError("runs must be at least 1")
    scores = []
    for run_number in range(1, runs + 1):
        result = evaluate_model(engine, dataset_path, client=client)
        scores.append({
            "run": run_number,
            "correct": result["correct"],
            "total": result["total"],
            "execution_accuracy": result["execution_accuracy"],
            "failed_ids": [item["id"] for item in result["results"] if not item["correct"]],
        })
    accuracies = [score["execution_accuracy"] for score in scores]
    return {
        "runs": scores,
        "mean_execution_accuracy": sum(accuracies) / len(accuracies),
        "min_execution_accuracy": min(accuracies),
        "max_execution_accuracy": max(accuracies),
    }
