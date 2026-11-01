"""Verify every adversarial SQL case is rejected before execution."""

import json
from pathlib import Path

import pytest

from text_to_sql.sql_validation import validate_read_only_sql


def test_adversarial_cases_are_rejected():
    path = Path(__file__).parents[1] / "eval" / "safety_cases.json"
    cases = json.loads(path.read_text(encoding="utf-8"))

    assert len(cases) == 7
    for case in cases:
        try:
            validate_read_only_sql(case["sql"])
        except ValueError:
            continue
        pytest.fail(f"Accepted unsafe SQL case {case['id']}: {case['sql']}")
