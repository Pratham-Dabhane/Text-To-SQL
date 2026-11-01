"""Tests for SQL-to-question alignment contracts."""

import pytest

from text_to_sql.alignment import build_alignment_prompt, parse_alignment_response


def test_alignment_prompt_contains_both_inputs():
    prompt = build_alignment_prompt("List customers", "SELECT full_name FROM customers")
    assert "List customers" in prompt
    assert "SELECT full_name FROM customers" in prompt


def test_alignment_response_requires_boolean_and_explanation():
    assert parse_alignment_response('{"aligned": true, "explanation": "Matches."}') == {
        "aligned": True,
        "explanation": "Matches.",
    }
    with pytest.raises(ValueError):
        parse_alignment_response('{"aligned": "yes"}')


def test_judge_alignment_uses_client():
    class FakeClient:
        def generate(self, prompt, *, json_mode=False):
            assert "List customers" in prompt
            assert json_mode is True
            return '{"aligned": true, "explanation": "The query lists customers."}'

    from text_to_sql.alignment import judge_alignment

    assert judge_alignment("List customers", "SELECT full_name FROM customers", FakeClient())["aligned"]
