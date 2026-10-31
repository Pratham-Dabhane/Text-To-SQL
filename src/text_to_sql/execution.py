"""Execute validated SQL inside a PostgreSQL read-only transaction."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from text_to_sql.audit import AuditLog
from text_to_sql.sql_guardrails import apply_row_limit, reject_large_estimate


def execute_read_only(
    engine: Engine,
    sql: str,
    *,
    max_rows: int = 1000,
    max_estimated_rows: int = 100_000,
    audit_log: AuditLog | None = None,
) -> dict[str, Any]:
    """Guard and execute SQL, returning a serializable result package."""
    try:
        guarded_sql = apply_row_limit(sql, max_rows)
        reject_large_estimate(engine, guarded_sql, max_estimated_rows)
    except ValueError as exc:
        if audit_log is not None:
            audit_log.record(sql, False, str(exc))
        raise

    with engine.connect() as connection:
        with connection.begin():
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
            result = connection.execute(text(guarded_sql))
            rows = [dict(row._mapping) for row in result]

    if audit_log is not None:
        audit_log.record(guarded_sql, True)

    return {
        "sql": guarded_sql,
        "columns": list(result.keys()),
        "rows": rows,
        "row_count": len(rows),
    }
