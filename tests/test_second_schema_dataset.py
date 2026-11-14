import json
from pathlib import Path


def test_second_schema_dataset_has_ten_cases():
    path = Path(__file__).parents[1] / "eval" / "second_schema_questions.json"
    cases = json.loads(path.read_text(encoding="utf-8"))
    assert len(cases) == 10
    assert len({case["id"] for case in cases}) == 10
    assert all(case["sql"].lstrip().upper().startswith("SELECT") for case in cases)
