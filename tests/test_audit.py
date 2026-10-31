"""Tests for query decision auditing."""

from text_to_sql.audit import AuditLog


def test_audit_log_records_allowed_and_blocked_decisions():
    log = AuditLog()
    log.record("SELECT 1", True)
    log.record("DELETE FROM customers", False, "write query")

    assert log.events == [
        {"sql": "SELECT 1", "allowed": True, "reason": None},
        {"sql": "DELETE FROM customers", "allowed": False, "reason": "write query"},
    ]
