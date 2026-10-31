"""Tests for configurable query row limits."""

import pytest

from text_to_sql.sql_guardrails import apply_row_limit, reject_large_estimate


def test_adds_limit_when_missing():
    assert apply_row_limit("SELECT * FROM customers", max_rows=10).endswith("LIMIT 10")


def test_reduces_excessive_limit_but_keeps_smaller_limit():
    assert apply_row_limit("SELECT * FROM customers LIMIT 5000", 1000).endswith("LIMIT 1000")
    assert apply_row_limit("SELECT * FROM customers LIMIT 5", 1000).endswith("LIMIT 5")


def test_rejects_invalid_configuration():
    with pytest.raises(ValueError, match="at least 1"):
        apply_row_limit("SELECT 1", 0)


class FakeResult:
    def scalar_one(self):
        return [{"Plan": {"Plan Rows": 200}}]


class FakeConnection:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, statement):
        return FakeResult()


class FakeEngine:
    def connect(self):
        return FakeConnection()


def test_rejects_large_explain_estimate():
    with pytest.raises(ValueError, match="exceeds limit"):
        reject_large_estimate(FakeEngine(), "SELECT 1", max_estimated_rows=100)
