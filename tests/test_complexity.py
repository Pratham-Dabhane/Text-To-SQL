"""Tests for multi-query validation routing hints."""

from text_to_sql.complexity import needs_multi_query_validation


def test_aggregation_is_complex():
    assert needs_multi_query_validation("What is total revenue by product?")


def test_simple_lookup_is_not_complex():
    assert not needs_multi_query_validation("List customers in Mumbai.")
