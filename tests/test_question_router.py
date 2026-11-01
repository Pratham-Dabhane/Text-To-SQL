"""Tests for pre-generation clarification decisions."""

import pytest

from text_to_sql.question_router import route_question


def test_router_clarifies_ambiguous_revenue():
    result = route_question("What is our revenue?")
    assert result["action"] == "clarify"
    assert len(result["options"]) == 2


def test_router_refuses_missing_profit_data():
    assert route_question("What was our profit last month?")["action"] == "refuse_unanswerable"


def test_router_allows_specific_sql_question():
    assert route_question("List customers in Mumbai.") == {"action": "generate_sql"}


def test_router_rejects_blank_question():
    with pytest.raises(ValueError):
        route_question(" ")
