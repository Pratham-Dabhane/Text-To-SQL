"""Runtime settings loaded once at application startup."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str | None
    history_db_path: str
    ollama_url: str
    api_key: str | None
    rate_limit_per_minute: int

    @classmethod
    def from_environment(cls) -> "Settings":
        rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        if rate_limit < 1:
            raise ValueError("RATE_LIMIT_PER_MINUTE must be at least 1.")
        return cls(
            database_url=os.getenv("DATABASE_URL"),
            history_db_path=os.getenv("HISTORY_DB_PATH", "data/history.sqlite3"),
            ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            api_key=os.getenv("API_KEY") or None,
            rate_limit_per_minute=rate_limit,
        )
