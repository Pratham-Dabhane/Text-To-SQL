"""API tests that do not require PostgreSQL or Ollama."""

from text_to_sql.api import QueryRequest, create_app


def test_ambiguous_question_returns_clarification():
    app = create_app()
    endpoint = next(route.endpoint for route in app.routes if route.path == "/v1/query")
    response = endpoint(QueryRequest(question="What is our revenue?"))

    assert response["action"] == "clarify"


def test_history_records_early_decisions():
    app = create_app()
    endpoint = next(route.endpoint for route in app.routes if route.path == "/v1/query")
    history_endpoint = next(route.endpoint for route in app.routes if route.path == "/v1/history")
    endpoint(QueryRequest(question="What is our revenue?"))

    assert history_endpoint()["items"][0]["action"] == "clarify"
