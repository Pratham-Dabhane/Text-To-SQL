"""Conservative post-execution result sanity checks."""

from __future__ import annotations

from typing import Any


def check_result_sanity(rows: list[dict[str, Any]], columns: list[str]) -> dict[str, Any]:
    """Return warnings without changing or rejecting query results."""
    warnings: list[str] = []
    if not rows:
        warnings.append("Query returned no rows.")
    for column in columns:
        if rows and all(row.get(column) is None for row in rows):
            warnings.append(f"Column '{column}' is NULL for every returned row.")
    return {"passed": not warnings, "warnings": warnings}
