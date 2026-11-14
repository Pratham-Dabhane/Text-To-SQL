"""Execute the application query workflow outside the HTTP layer."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import uuid4

from sqlalchemy.engine import Engine

from text_to_sql.execution import execute_read_only
from text_to_sql.generation import generate_validated_sql
from text_to_sql.history_store import HistoryStore
from text_to_sql.ollama_client import OllamaClient
from text_to_sql.question_router import route_question
from text_to_sql.schema import inspect_schema
from text_to_sql.schema_prompt import format_schema_for_prompt


class QueryPipeline:
    """Route, generate, safely execute, and persist one user question."""

    def __init__(
        self,
        engine_provider: Callable[[], Engine],
        client: OllamaClient,
        history_store: HistoryStore,
    ) -> None:
        self.engine_provider = engine_provider
        self.client = client
        self.history_store = history_store

    def run(self, question: str) -> dict[str, Any]:
        decision = route_question(question)
        if decision["action"] != "generate_sql":
            return self._record(question, decision)

        engine = self.engine_provider()
        schema_text = format_schema_for_prompt(inspect_schema(engine))
        _, validated_sql = generate_validated_sql(
            question, schema_text, self.client
        )
        result = execute_read_only(engine, validated_sql)
        return self._record(
            question,
            {
                "action": "executed",
                "generated_sql": validated_sql,
                "result": result,
            },
        )

    def _record(self, question: str, response: dict[str, Any]) -> dict[str, Any]:
        query_id = str(uuid4())
        recorded = {"query_id": query_id, **response}
        self.history_store.add(query_id, question, recorded)
        return recorded
