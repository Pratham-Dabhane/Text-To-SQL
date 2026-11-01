"""Run golden SQL cases and calculate measured execution accuracy."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy.engine import Engine

from text_to_sql.execution import execute_read_only


def _normalise(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def rows_match(actual: list[dict[str, Any]], columns: list[str], expected: list[list[Any]]) -> bool:
    actual_rows = [
        [_normalise(row[column]) for column in columns]
        for row in actual
    ]
    return actual_rows == [[_normalise(value) for value in row] for row in expected]


def result_shape_matches(columns: list[str], expected: list[list[Any]]) -> bool:
    """Check the deterministic number of returned columns."""
    return not expected or len(columns) == len(expected[0])


def evaluate_dataset(engine: Engine, dataset_path: str | Path) -> dict[str, Any]:
    cases = json.loads(Path(dataset_path).read_text(encoding="utf-8"))
    results = []
    for case in cases:
        output = execute_read_only(engine, case["sql"])
        correct = rows_match(output["rows"], output["columns"], case["expected_rows"])
        results.append({"id": case["id"], "correct": correct})

    correct_count = sum(result["correct"] for result in results)
    return {
        "total": len(results),
        "correct": correct_count,
        "execution_accuracy": correct_count / len(results) if results else 0.0,
        "results": results,
    }
