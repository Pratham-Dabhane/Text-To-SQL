import json
from pathlib import Path


def test_independent_dataset_has_twenty_unique_cases():
    path = Path(__file__).parents[1] / "eval" / "independent_questions.json"
    cases = json.loads(path.read_text(encoding="utf-8"))

    assert len(cases) == 20
    assert len({case["id"] for case in cases}) == 20
    for case in cases:
        assert case["question"]
        assert case["sql"].lstrip().upper().startswith("SELECT")
        assert isinstance(case["expected_rows"], list)
