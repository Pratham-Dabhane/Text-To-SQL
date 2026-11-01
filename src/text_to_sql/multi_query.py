"""Compare independent query results as one correctness signal."""

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Engine

from text_to_sql.execution import execute_read_only


def compare_results(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    """Return whether two result packages have the same columns and rows."""
    same_columns = first.get("columns") == second.get("columns")
    same_rows = first.get("rows") == second.get("rows")
    return {
        "agree": same_columns and same_rows,
        "same_columns": same_columns,
        "same_rows": same_rows,
    }


def execute_and_compare(
    engine: Engine, first_sql: str, second_sql: str
) -> dict[str, Any]:
    """Safely execute two approaches and compare their result packages."""
    first = execute_read_only(engine, first_sql)
    second = execute_read_only(engine, second_sql)
    return {
        "comparison": compare_results(first, second),
        "first": first,
        "second": second,
    }
