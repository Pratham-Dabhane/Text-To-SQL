"""Minimal client for a local Ollama generate endpoint."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OllamaClient:
    """Send prompts to Ollama running on the local machine."""

    def __init__(
        self,
        model: str = "llama3.2:3b",
        base_url: str | None = None,
        timeout_seconds: float = 60.0,
        temperature: float = 0.0,
    ) -> None:
        self.model = model
        self.base_url = (base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.temperature = temperature

    def generate(self, prompt: str, *, json_mode: bool = False) -> str:
        """Return Ollama's generated text for one prompt."""
        if not prompt.strip():
            raise ValueError("Prompt must not be blank.")

        request_body = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": self.temperature},
        }
        if json_mode:
            request_body["format"] = "json"
        body = json.dumps(request_body).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError) as exc:
            raise RuntimeError(f"Could not reach Ollama: {exc}") from exc

        generated = payload.get("response")
        if not isinstance(generated, str):
            raise RuntimeError("Ollama response did not contain text.")
        return generated.strip()
