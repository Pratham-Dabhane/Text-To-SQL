"""Small SQLite-backed store for API history and user feedback."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class HistoryStore:
    def __init__(self, path: str | Path = "data/history.sqlite3") -> None:
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS query_history (
                    query_id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    feedback TEXT
                )"""
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def add(self, query_id: str, question: str, payload: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO query_history (query_id, question, payload) VALUES (?, ?, ?)",
                (query_id, question, json.dumps(payload, default=str)),
            )

    def add_feedback(self, query_id: str, feedback: str) -> bool:
        with self._connect() as connection:
            result = connection.execute(
                "UPDATE query_history SET feedback = ? WHERE query_id = ?",
                (feedback, query_id),
            )
            return result.rowcount == 1

    def list(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT question, payload, feedback FROM query_history ORDER BY rowid"
            ).fetchall()
        items = []
        for row in rows:
            item = {"question": row["question"], **json.loads(row["payload"])}
            if row["feedback"]:
                item["feedback"] = row["feedback"]
            items.append(item)
        return items
