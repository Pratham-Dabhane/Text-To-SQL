"""Minimal FastAPI interface for the safe query pipeline."""

from __future__ import annotations

import os
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from text_to_sql.execution import execute_read_only
from text_to_sql.ollama_client import OllamaClient
from text_to_sql.schema import inspect_schema
from text_to_sql.schema_prompt import format_schema_for_prompt
from text_to_sql.sql_response import clean_generated_sql
from text_to_sql.sql_validation import validate_read_only_sql
from text_to_sql.query_pipeline import prepare_query
from text_to_sql.question_router import route_question
from text_to_sql.history_store import HistoryStore


class QueryRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    query_id: str
    is_correct: bool


def create_app(engine: Engine | None = None, client: OllamaClient | None = None, history_store: HistoryStore | None = None) -> FastAPI:
    app = FastAPI(title="Safe Text-to-SQL")
    database_engine = engine
    model_client = client or OllamaClient()
    store = history_store or HistoryStore(os.getenv("HISTORY_DB_PATH", "data/history.sqlite3"))
    api_key = os.getenv("API_KEY")
    limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    requests_by_client: dict[str, list[float]] = {}

    @app.middleware("http")
    async def protect_api(request, call_next):
        if request.url.path.startswith("/v1/"):
            if api_key and request.headers.get("X-API-Key") != api_key:
                return JSONResponse({"detail": "Invalid API key."}, status_code=401)
            now = time.monotonic()
            client_id = request.client.host if request.client else "unknown"
            recent = [stamp for stamp in requests_by_client.get(client_id, []) if now - stamp < 60]
            if len(recent) >= limit:
                return JSONResponse({"detail": "Rate limit exceeded."}, status_code=429)
            recent.append(now)
            requests_by_client[client_id] = recent
        return await call_next(request)

    def get_engine() -> Engine:
        nonlocal database_engine
        if database_engine is None:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise HTTPException(500, "DATABASE_URL is not configured.")
            database_engine = create_engine(database_url)
        return database_engine

    @app.get("/v1/schema")
    def schema():
        return inspect_schema(get_engine())

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/v1/history")
    def get_history():
        return {"items": store.list()}

    @app.post("/v1/feedback")
    def submit_feedback(request: FeedbackRequest):
        feedback = "correct" if request.is_correct else "incorrect"
        if not store.add_feedback(request.query_id, feedback):
            raise HTTPException(404, "Query was not found in this session.")
        return {"query_id": request.query_id, "feedback": feedback}

    @app.post("/v1/query")
    def query(request: QueryRequest):
        early_decision = route_question(request.question)
        if early_decision["action"] != "generate_sql":
            response = {"query_id": str(uuid4()), **early_decision}
            store.add(response["query_id"], request.question, response)
            return response

        try:
            database_engine = get_engine()
            schema_text = format_schema_for_prompt(inspect_schema(database_engine))
            prepared = prepare_query(request.question, schema_text)
            generated = model_client.generate(prepared["prompt"])
            sql = validate_read_only_sql(clean_generated_sql(generated))
            result = execute_read_only(database_engine, sql)
            response = {
                "query_id": str(uuid4()),
                "action": "executed",
                "generated_sql": sql,
                "result": result,
            }
            store.add(response["query_id"], request.question, response)
            return response
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(503, str(exc)) from exc

    return app


app = create_app()
