"""Tests for independent result comparison."""

from text_to_sql.multi_query import compare_results


def test_matching_results_agree():
    result = {"columns": ["count"], "rows": [{"count": 2}]}
    assert compare_results(result, result)["agree"]


def test_different_results_do_not_agree():
    first = {"columns": ["count"], "rows": [{"count": 2}]}
    second = {"columns": ["count"], "rows": [{"count": 3}]}
    comparison = compare_results(first, second)
    assert comparison["agree"] is False
    assert comparison["same_columns"] is True
    assert comparison["same_rows"] is False
