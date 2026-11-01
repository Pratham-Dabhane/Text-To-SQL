"""Tests for non-blocking result sanity checks."""

from text_to_sql.sanity import check_result_sanity


def test_sanity_warns_for_empty_results():
    result = check_result_sanity([], ["name"])
    assert result["passed"] is False
    assert result["warnings"]


def test_sanity_warns_for_all_null_column():
    result = check_result_sanity([{"name": None}], ["name"])
    assert "NULL" in result["warnings"][0]


def test_sanity_accepts_normal_rows():
    assert check_result_sanity([{"name": "Asha"}], ["name"])["passed"]
