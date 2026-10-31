"""Read PostgreSQL schema metadata with SQLAlchemy.

This module deliberately reads metadata only. It does not execute application
queries or retrieve rows from the customers, orders, or products tables.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import inspect
from sqlalchemy.engine import Engine


def inspect_schema(engine: Engine) -> dict[str, Any]:
    """Return tables, columns, primary keys, and foreign keys for an engine.

    SQLAlchemy's Inspector asks the database for its system metadata. The
    returned dictionary contains only schema information and can later be
    formatted into context for a text-to-SQL model.
    """
    inspector = inspect(engine)
    tables: dict[str, Any] = {}

    for table_name in inspector.get_table_names():
        columns = [
            {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"],
            }
            for column in inspector.get_columns(table_name)
        ]
        primary_key = inspector.get_pk_constraint(table_name)["constrained_columns"]
        foreign_keys = [
            {
                "columns": foreign_key["constrained_columns"],
                "referred_table": foreign_key["referred_table"],
                "referred_columns": foreign_key["referred_columns"],
            }
            for foreign_key in inspector.get_foreign_keys(table_name)
        ]

        tables[table_name] = {
            "columns": columns,
            "primary_key": primary_key,
            "foreign_keys": foreign_keys,
        }

    return {"tables": tables}
