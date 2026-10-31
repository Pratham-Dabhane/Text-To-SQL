"""Tests that unsafe SQL is rejected before execution."""

import os

import pytest
from sqlalchemy import create_engine

from text_to_sql.audit import AuditLog
from text_to_sql.execution import execute_read_only


class UnusedEngine:
    def connect(self):
        raise AssertionError("The database must not be contacted for unsafe SQL.")


def test_unsafe_sql_is_rejected_before_connection():
    log = AuditLog()
    with pytest.raises(ValueError, match="Only read-only SELECT"):
        execute_read_only(UnusedEngine(), "DELETE FROM customers", audit_log=log)
    assert log.events[0]["allowed"] is False


def test_safe_query_executes_in_live_database():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("Set DATABASE_URL to run PostgreSQL integration tests.")

    from text_to_sql.execution import execute_read_only

    engine = create_engine(database_url)
    try:
        result = execute_read_only(
            engine, "SELECT full_name FROM customers ORDER BY full_name"
        )
    finally:
        engine.dispose()

    assert result["columns"] == ["full_name"]
    assert result["row_count"] == 6
