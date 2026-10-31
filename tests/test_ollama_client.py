"""Unit tests for the local Ollama client; no Ollama process is required."""

import json

import pytest

import text_to_sql.ollama_client as ollama_client


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def test_generate_posts_model_and_prompt(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse({"response": "SELECT 1;"})

    monkeypatch.setattr(ollama_client, "urlopen", fake_urlopen)
    result = ollama_client.OllamaClient().generate("Return SQL only.")

    assert result == "SELECT 1;"
    assert captured["body"] == {
        "model": "llama3.2:3b",
        "prompt": "Return SQL only.",
        "stream": False,
    }


def test_generate_rejects_blank_prompt():
    with pytest.raises(ValueError, match="must not be blank"):
        ollama_client.OllamaClient().generate("  ")
