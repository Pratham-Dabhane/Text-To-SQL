"""Build and parse SQL-to-question alignment judgments."""

from __future__ import annotations

import json
from typing import Any

from text_to_sql.ollama_client import OllamaClient


def build_alignment_prompt(question: str, sql: str) -> str:
    """Ask a model to compare a question with generated SQL."""
    if not question.strip() or not sql.strip():
        raise ValueError("Question and SQL must not be blank.")
    return f"""You are reviewing SQL, not generating SQL.
Decide whether the SQL answers the original question.
Your response itself must be JSON only with exactly these fields:
{{"aligned": true or false, "explanation": "short explanation"}}
Example: {{"aligned": true, "explanation": "The SQL filters customers by Mumbai."}}
Do not output SQL. Do not modify the SQL. Do not use confidence scores or probabilities.

<question>
{question.strip()}
</question>
<sql>
{sql.strip()}
</sql>"""


def parse_alignment_response(response: str) -> dict[str, Any]:
    """Validate a model's structured alignment response."""
    try:
        result = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError("Alignment response must be valid JSON.") from exc
    if not isinstance(result.get("aligned"), bool) or not isinstance(
        result.get("explanation"), str
    ):
        raise ValueError("Alignment response has invalid fields.")
    return {"aligned": result["aligned"], "explanation": result["explanation"]}


def judge_alignment(question: str, sql: str, client: OllamaClient) -> dict[str, Any]:
    """Ask Ollama for a structured alignment review."""
    return parse_alignment_response(
        client.generate(build_alignment_prompt(question, sql), json_mode=True)
    )
