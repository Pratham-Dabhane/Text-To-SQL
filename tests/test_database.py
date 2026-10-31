"""Smoke tests for the local Phase 1 database.

Set DATABASE_URL before running pytest. These tests are read-only and expect
the schema and sample rows from db/schema.sql and db/seed.sql to be loaded.
"""

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.fixture(scope="module")
def connection():
    if not DATABASE_URL:
        pytest.skip("Set DATABASE_URL to run PostgreSQL integration tests.")

    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as conn:
            yield conn
    except SQLAlchemyError as exc:
        pytest.fail(f"Could not connect to PostgreSQL: {exc}")
    finally:
        engine.dispose()


def test_expected_tables_and_seed_counts(connection):
    counts = connection.execute(
        text(
            "SELECT "
            "(SELECT count(*) FROM customers), "
            "(SELECT count(*) FROM products), "
            "(SELECT count(*) FROM orders)"
        )
    ).one()

    assert counts == (6, 5, 11)


def test_order_foreign_keys_have_matching_rows(connection):
    orphan_count = connection.execute(
        text(
            "SELECT count(*) FROM orders o "
            "LEFT JOIN customers c ON c.customer_id = o.customer_id "
            "LEFT JOIN products p ON p.product_id = o.product_id "
            "WHERE c.customer_id IS NULL OR p.product_id IS NULL"
        )
    ).scalar_one()

    assert orphan_count == 0
