"""Evaluate local LLM-generated SQL against the golden dataset."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from sqlalchemy.engine import Engine

from eval.evaluator import rows_match
from text_to_sql.execution import execute_read_only
from text_to_sql.ollama_client import OllamaClient
from text_to_sql.prompt import build_sql_generation_prompt
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
) -> dict[str, Any]:
    cases = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    schema_text = format_schema_for_prompt(inspect_schema(engine))
    model_client = client or OllamaClient()
    results = []

    for case in cases:
        generated = None
        try:
            prompt = build_sql_generation_prompt(case["question"], schema_text)
            generated = model_client.generate(prompt)
            cleaned = clean_generated_sql(generated)
            validated = validate_read_only_sql(cleaned)
            output = execute_read_only(engine, validated)
            correct = rows_match(output["rows"], output["columns"], case["expected_rows"])
            results.append({
                "id": case["id"],
                "correct": correct,
                "generated_sql": generated,
                "validated_sql": validated,
            })
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
