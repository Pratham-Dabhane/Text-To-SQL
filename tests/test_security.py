from text_to_sql.security import ApiSecurity


def test_security_rejects_invalid_api_key_without_consuming_rate_limit():
    security = ApiSecurity("secret", 1, clock=lambda: 10)

    assert security.reject_reason("client", None) == (401, "Invalid API key.")
    assert security.reject_reason("client", "secret") is None


def test_security_limits_requests_per_client():
    now = [10.0]
    security = ApiSecurity(None, 1, clock=lambda: now[0])

    assert security.reject_reason("first", None) is None
    assert security.reject_reason("first", None) == (429, "Rate limit exceeded.")
    assert security.reject_reason("second", None) is None

    now[0] = 71.0
    assert security.reject_reason("first", None) is None
