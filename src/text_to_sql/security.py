"""Small in-memory API-key and rate-limit policy."""

from __future__ import annotations

import time
from collections.abc import Callable


class ApiSecurity:
    def __init__(
        self,
        api_key: str | None,
        requests_per_minute: int,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.api_key = api_key
        self.requests_per_minute = requests_per_minute
        self.clock = clock
        self.requests_by_client: dict[str, list[float]] = {}

    def reject_reason(self, client_id: str, supplied_api_key: str | None) -> tuple[int, str] | None:
        if self.api_key and supplied_api_key != self.api_key:
            return 401, "Invalid API key."

        now = self.clock()
        recent = [
            stamp
            for stamp in self.requests_by_client.get(client_id, [])
            if now - stamp < 60
        ]
        if len(recent) >= self.requests_per_minute:
            return 429, "Rate limit exceeded."
        recent.append(now)
        self.requests_by_client[client_id] = recent
        return None
