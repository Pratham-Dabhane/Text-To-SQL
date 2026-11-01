"""Small pre-generation router for known ambiguity and schema gaps."""

from __future__ import annotations


def route_question(question: str) -> dict[str, object]:
    """Return a decision before SQL generation for obvious unsafe guesses.

    This is intentionally conservative and domain-specific; it is a baseline,
    not a general natural-language ambiguity detector.
    """
    text = question.strip().lower()
    if not text:
        raise ValueError("Question must not be blank.")
    if "profit" in text or "cost" in text:
        return {
            "action": "refuse_unanswerable",
            "reason": "The current schema has no profit or cost data.",
        }
    if "revenue" in text and not any(term in text for term in ("delivered", "all orders")):
        return {
            "action": "clarify",
            "reason": "Revenue could mean all orders or delivered orders.",
            "options": ["Revenue from all orders", "Revenue from delivered orders"],
        }
    if "valuable" in text:
        return {
            "action": "clarify",
            "reason": "The ranking metric is not specified.",
            "options": ["Highest delivered revenue", "Most orders"],
        }
    return {"action": "generate_sql"}
