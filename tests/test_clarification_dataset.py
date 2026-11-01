"""Checks for ambiguity and unanswerable-question cases."""

import json
from pathlib import Path


def test_clarification_cases_have_supported_actions():
    path = Path(__file__).parents[1] / "eval" / "clarification_cases.json"
    cases = json.loads(path.read_text(encoding="utf-8"))

    assert len(cases) == 3
    assert {case["expected_action"] for case in cases} == {
        "clarify",
        "refuse_unanswerable",
    }
    assert all(case["reason"] for case in cases)
