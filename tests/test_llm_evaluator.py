"""Unit tests for scoring generated SQL without calling an LLM."""

from eval.llm_evaluator import score_generated_sql


def test_score_generated_sql_uses_execution_results():
    case = {"expected_rows": [[2]]}

    def fake_executor(sql):
        assert sql == "SELECT 2"
        return {"columns": ["?column?"], "rows": [{"?column?": 2}]}

    assert score_generated_sql(case, "```sql\nSELECT 2\n```", fake_executor)
