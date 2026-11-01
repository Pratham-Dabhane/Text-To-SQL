"""API tests that do not require PostgreSQL or Ollama."""

from text_to_sql.api import QueryRequest, create_app
from text_to_sql.history_store import HistoryStore


def test_ambiguous_question_returns_clarification(tmp_path):
    app = create_app(history_store=HistoryStore(tmp_path / "history.sqlite3"))
    endpoint = next(route.endpoint for route in app.routes if route.path == "/v1/query")
    response = endpoint(QueryRequest(question="What is our revenue?"))

    assert response["action"] == "clarify"


def test_history_records_early_decisions(tmp_path):
    app = create_app(history_store=HistoryStore(tmp_path / "history.sqlite3"))
    endpoint = next(route.endpoint for route in app.routes if route.path == "/v1/query")
    history_endpoint = next(route.endpoint for route in app.routes if route.path == "/v1/history")
    endpoint(QueryRequest(question="What is our revenue?"))

    assert history_endpoint()["items"][0]["action"] == "clarify"


def test_feedback_attaches_to_query_history(tmp_path):
    app = create_app(history_store=HistoryStore(tmp_path / "history.sqlite3"))
    query_endpoint = next(route.endpoint for route in app.routes if route.path == "/v1/query")
    feedback_endpoint = next(route.endpoint for route in app.routes if route.path == "/v1/feedback")
    from text_to_sql.api import FeedbackRequest

    query = query_endpoint(QueryRequest(question="What is our revenue?"))
    response = feedback_endpoint(FeedbackRequest(query_id=query["query_id"], is_correct=False))

    assert response["feedback"] == "incorrect"


def test_health_endpoint_returns_ok(tmp_path):
    app = create_app(history_store=HistoryStore(tmp_path / "history.sqlite3"))
    endpoint = next(route.endpoint for route in app.routes if route.path == "/health")

    assert endpoint() == {"status": "ok"}
