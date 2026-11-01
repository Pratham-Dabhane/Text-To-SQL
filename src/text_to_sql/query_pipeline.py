"""Prepare a question for generation or return an early decision."""

from __future__ import annotations

from typing import Any

from text_to_sql.prompt import build_sql_generation_prompt
from text_to_sql.question_router import route_question


def prepare_query(question: str, schema_text: str) -> dict[str, Any]:
    """Route ambiguity first; build an LLM prompt only when appropriate."""
    decision = route_question(question)
    if decision["action"] != "generate_sql":
        return decision
    return {
        "action": "generate_sql",
        "prompt": build_sql_generation_prompt(question, schema_text),
    }
