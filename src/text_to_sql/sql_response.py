"""Normalize SQL text returned by a language model."""

from __future__ import annotations

import re


def clean_generated_sql(response: str) -> str:
    """Remove optional Markdown fences and return one SQL text value."""
    if not response.strip():
        raise ValueError("Generated SQL must not be blank.")

    cleaned = response.strip()
    fenced = re.fullmatch(r"```(?:sql)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()

    if not cleaned:
        raise ValueError("Generated SQL must not be blank.")
    return cleaned
