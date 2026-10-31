"""Unit tests for golden-result comparison."""

from eval.evaluator import rows_match


def test_rows_match_compares_columns_in_result_order():
    actual = [{"name": "Asha", "count": 2}]
    assert rows_match(actual, ["name", "count"], [["Asha", 2]])


def test_rows_match_rejects_different_values():
    actual = [{"name": "Asha", "count": 2}]
    assert not rows_match(actual, ["name", "count"], [["Asha", 3]])
