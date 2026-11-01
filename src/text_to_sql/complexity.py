"""Small routing heuristic for deciding when independent validation may help."""

from __future__ import annotations


def needs_multi_query_validation(question: str) -> bool:
    """Return whether a question contains patterns that merit a second approach."""
    text = question.lower()
    indicators = (
        "each ",
        "per ",
        "average",
        "total",
        "highest",
        "lowest",
        "between",
        "by month",
    )
    return any(indicator in text for indicator in indicators)
