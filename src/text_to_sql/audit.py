"""Small audit log for query decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AuditEvent:
    sql: str
    allowed: bool
    reason: str | None = None


class AuditLog:
    """In-memory audit sink for the learning application."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def record(self, sql: str, allowed: bool, reason: str | None = None) -> None:
        self.events.append(asdict(AuditEvent(sql, allowed, reason)))
