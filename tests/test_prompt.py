"""Unit tests for SQL-generation prompt construction."""

import pytest

from text_to_sql.prompt import build_sql_generation_prompt


def test_prompt_includes_question_schema_and_rules():
    prompt = build_sql_generation_prompt(
        "List customers in Mumbai.", "TABLE customers\n  city TEXT"
    )

    assert "List customers in Mumbai." in prompt
    assert "TABLE customers" in prompt
    assert "Return SQL only." in prompt
    assert "Do not use INSERT" in prompt


@pytest.mark.parametrize("question,schema_text", [("", "TABLE customers"), ("List customers", "")])
def test_prompt_rejects_blank_inputs(question, schema_text):
    with pytest.raises(ValueError):
        build_sql_generation_prompt(question, schema_text)
