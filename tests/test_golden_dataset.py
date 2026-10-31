"""Structural checks for the initial golden evaluation dataset."""

import json
from pathlib import Path


def test_golden_dataset_has_ten_unique_cases():
    path = Path(__file__).parents[1] / "eval" / "golden_questions.json"
    cases = json.loads(path.read_text(encoding="utf-8"))

    assert len(cases) == 10
    assert len({case["id"] for case in cases}) == 10
    for case in cases:
        assert case["question"]
        assert case["sql"].lstrip().upper().startswith("SELECT")
        assert isinstance(case["expected_rows"], list)
