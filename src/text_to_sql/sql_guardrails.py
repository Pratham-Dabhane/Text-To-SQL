"""Configurable guardrails applied after read-only SQL validation."""

from __future__ import annotations

import sqlglot
from sqlglot import exp
from sqlalchemy import text
from sqlalchemy.engine import Engine

from text_to_sql.sql_validation import validate_read_only_sql


def apply_row_limit(sql: str, max_rows: int = 1000) -> str:
    """Ensure one validated SELECT returns no more than ``max_rows`` rows."""
    if max_rows < 1:
        raise ValueError("max_rows must be at least 1.")

    validated = validate_read_only_sql(sql)
    statement = sqlglot.parse_one(validated, read="postgres")
    limit = statement.args.get("limit")

    if limit is None:
        statement.set("limit", exp.Limit(expression=exp.Literal.number(max_rows)))
    else:
        expression = limit.args.get("expression")
        if not isinstance(expression, exp.Literal) or not expression.is_int:
            raise ValueError("LIMIT must be an integer.")
        if int(expression.this) > max_rows:
            limit.set("expression", exp.Literal.number(max_rows))

    return statement.sql(dialect="postgres")


def estimated_rows(engine: Engine, sql: str) -> int:
    """Return PostgreSQL's estimated top-level row count without executing SQL."""
    validated = validate_read_only_sql(sql)
    with engine.connect() as connection:
        plan = connection.execute(text(f"EXPLAIN (FORMAT JSON) {validated}")).scalar_one()
    return int(plan[0]["Plan"]["Plan Rows"])


def reject_large_estimate(engine: Engine, sql: str, max_estimated_rows: int = 100_000) -> int:
    """Raise when PostgreSQL estimates more than the configured row count."""
    if max_estimated_rows < 1:
        raise ValueError("max_estimated_rows must be at least 1.")
    rows = estimated_rows(engine, sql)
    if rows > max_estimated_rows:
        raise ValueError(
            f"Estimated result size {rows} exceeds limit {max_estimated_rows}."
        )
    return rows
