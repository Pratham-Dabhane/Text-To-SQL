"""Tests for structural SQL validation."""

import pytest

from text_to_sql.sql_validation import validate_read_only_sql


def test_select_is_accepted_and_normalized():
    assert validate_read_only_sql("select full_name from customers") == (
        "SELECT full_name FROM customers"
    )


@pytest.mark.parametrize(
    "sql",
    ["DELETE FROM customers", "DROP TABLE customers", "SELECT 1; SELECT 2"],
)
def test_writes_and_multiple_statements_are_rejected(sql):
    with pytest.raises(ValueError):
        validate_read_only_sql(sql)


def test_malformed_sql_is_rejected():
    with pytest.raises(ValueError, match="Invalid PostgreSQL SQL"):
        validate_read_only_sql("SELECT FROM")
