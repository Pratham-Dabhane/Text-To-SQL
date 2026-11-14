import pytest

from text_to_sql.settings import Settings


def test_settings_reads_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "12")

    settings = Settings.from_environment()

    assert settings.database_url == "postgresql://example"
    assert settings.api_key == "test-key"
    assert settings.rate_limit_per_minute == 12


def test_settings_rejects_non_positive_rate_limit(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "0")

    with pytest.raises(ValueError, match="at least 1"):
        Settings.from_environment()
