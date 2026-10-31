"""Unit tests for model SQL response normalization."""

import pytest

from text_to_sql.sql_response import clean_generated_sql


def test_cleaner_preserves_plain_sql():
    assert clean_generated_sql("SELECT 1;") == "SELECT 1;"


def test_cleaner_removes_sql_markdown_fence():
    assert clean_generated_sql("```sql\nSELECT 1;\n```") == "SELECT 1;"


def test_cleaner_rejects_blank_response():
    with pytest.raises(ValueError, match="must not be blank"):
        clean_generated_sql(" ```sql\n\n``` ")
