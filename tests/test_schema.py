"""Integration tests for database schema introspection."""

import os

import pytest
from sqlalchemy import create_engine

from text_to_sql.schema import inspect_schema


DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.fixture(scope="module")
def schema():
    if not DATABASE_URL:
        pytest.skip("Set DATABASE_URL to run PostgreSQL integration tests.")

    engine = create_engine(DATABASE_URL)
    try:
        return inspect_schema(engine)
    finally:
        engine.dispose()


def test_schema_contains_expected_tables(schema):
    assert {"customers", "orders", "products"} <= set(schema["tables"])
    assert schema["tables"]["orders"]["primary_key"] == ["order_id"]


def test_orders_foreign_keys_describe_its_relationships(schema):
    foreign_keys = schema["tables"]["orders"]["foreign_keys"]

    assert {
        "columns": ["customer_id"],
        "referred_table": "customers",
        "referred_columns": ["customer_id"],
    } in foreign_keys
    assert {
        "columns": ["product_id"],
        "referred_table": "products",
        "referred_columns": ["product_id"],
    } in foreign_keys
