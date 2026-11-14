"""Shared schema-aware SQL generation and validation."""

from __future__ import annotations

from text_to_sql.ollama_client import OllamaClient
from text_to_sql.prompt import build_sql_generation_prompt
from text_to_sql.sql_response import clean_generated_sql
from text_to_sql.sql_validation import validate_read_only_sql


def generate_validated_sql(
    question: str, schema_text: str, client: OllamaClient
) -> tuple[str, str]:
    """Return raw model output and validated PostgreSQL SQL."""
    prompt = build_sql_generation_prompt(question, schema_text)
    generated_sql = client.generate(prompt)
    validated_sql = validate_read_only_sql(clean_generated_sql(generated_sql))
    return generated_sql, validated_sql
