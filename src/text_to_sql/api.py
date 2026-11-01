"""Minimal FastAPI interface for the safe query pipeline."""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
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


class QueryRequest(BaseModel):
    question: str


def create_app(engine: Engine | None = None, client: OllamaClient | None = None) -> FastAPI:
    app = FastAPI(title="Safe Text-to-SQL")
    database_engine = engine
    model_client = client or OllamaClient()
    history: list[dict[str, object]] = []

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

    @app.get("/v1/history")
    def get_history():
        return {"items": history}

    @app.post("/v1/query")
    def query(request: QueryRequest):
        early_decision = route_question(request.question)
        if early_decision["action"] != "generate_sql":
            history.append({"question": request.question, **early_decision})
            return early_decision

        try:
            database_engine = get_engine()
            schema_text = format_schema_for_prompt(inspect_schema(database_engine))
            prepared = prepare_query(request.question, schema_text)
            generated = model_client.generate(prepared["prompt"])
            sql = validate_read_only_sql(clean_generated_sql(generated))
            result = execute_read_only(database_engine, sql)
            response = {"action": "executed", "generated_sql": sql, "result": result}
            history.append({"question": request.question, **response})
            return response
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

    return app


app = create_app()
