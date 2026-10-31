"""Structural validation for generated PostgreSQL SQL."""

from __future__ import annotations

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


def validate_read_only_sql(sql: str) -> str:
    """Return normalized SQL or raise ValueError if it is not one read query."""
    if not sql.strip():
        raise ValueError("SQL must not be blank.")

    try:
        statements = sqlglot.parse(sql, read="postgres")
    except ParseError as exc:
        raise ValueError(f"Invalid PostgreSQL SQL: {exc}") from exc

    if len(statements) != 1:
        raise ValueError("Exactly one SQL statement is required.")

    statement = statements[0]
    allowed_roots = (exp.Select, exp.Union, exp.Intersect, exp.Except)
    if not isinstance(statement, allowed_roots):
        raise ValueError("Only read-only SELECT queries are allowed.")

    forbidden = (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Alter, exp.Drop)
    if any(isinstance(node, forbidden) for node in statement.walk()):
        raise ValueError("Write or schema-changing SQL is not allowed.")

    return statement.sql(dialect="postgres")
