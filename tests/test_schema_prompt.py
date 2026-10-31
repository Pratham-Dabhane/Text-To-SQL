"""Unit tests for converting schema metadata into prompt text."""

import pytest

from text_to_sql.schema_prompt import format_schema_for_prompt


SAMPLE_SCHEMA = {
    "tables": {
        "orders": {
            "columns": [
                {"name": "order_id", "type": "INTEGER", "nullable": False},
                {"name": "customer_id", "type": "INTEGER", "nullable": False},
            ],
            "primary_key": ["order_id"],
            "foreign_keys": [
                {
                    "columns": ["customer_id"],
                    "referred_table": "customers",
                    "referred_columns": ["customer_id"],
                }
            ],
        },
        "customers": {
            "columns": [
                {"name": "customer_id", "type": "INTEGER", "nullable": False},
                {"name": "full_name", "type": "TEXT", "nullable": False},
            ],
            "primary_key": ["customer_id"],
            "foreign_keys": [],
        },
    }
}


def test_formatter_includes_columns_keys_and_relationships():
    prompt_text = format_schema_for_prompt(SAMPLE_SCHEMA)

    assert "TABLE customers" in prompt_text
    assert "customer_id INTEGER NOT NULL PRIMARY KEY" in prompt_text
    assert "TABLE orders" in prompt_text
    assert "customer_id INTEGER NOT NULL REFERENCES customers.customer_id" in prompt_text
    assert prompt_text.index("TABLE customers") < prompt_text.index("TABLE orders")


def test_formatter_rejects_a_schema_without_tables():
    with pytest.raises(ValueError, match="non-empty 'tables' dictionary"):
        format_schema_for_prompt({})
