"""Tests for routing before LLM prompt construction."""

from text_to_sql.query_pipeline import prepare_query


def test_ambiguous_question_does_not_create_a_prompt():
    result = prepare_query("What is our revenue?", "TABLE orders")
    assert result["action"] == "clarify"
    assert "prompt" not in result


def test_specific_question_creates_a_prompt():
    result = prepare_query("List customers in Mumbai.", "TABLE customers")
    assert result["action"] == "generate_sql"
    assert "TABLE customers" in result["prompt"]
