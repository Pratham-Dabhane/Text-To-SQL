"""Tests for the application query workflow."""

from text_to_sql.history_store import HistoryStore
from text_to_sql.query_pipeline import QueryPipeline


class UnusedEngine:
    pass


class UnusedClient:
    pass


def test_ambiguous_question_does_not_contact_engine(tmp_path):
    pipeline = QueryPipeline(
        lambda: UnusedEngine(), UnusedClient(), HistoryStore(tmp_path / "history.sqlite3")
    )

    result = pipeline.run("What is our revenue?")

    assert result["action"] == "clarify"


def test_early_decision_is_persisted(tmp_path):
    store = HistoryStore(tmp_path / "history.sqlite3")
    pipeline = QueryPipeline(lambda: UnusedEngine(), UnusedClient(), store)

    result = pipeline.run("What is our revenue?")

    assert store.list()[0]["query_id"] == result["query_id"]
