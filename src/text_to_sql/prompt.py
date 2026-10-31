"""Build consistent text-to-SQL prompts."""


def build_sql_generation_prompt(question: str, schema_text: str) -> str:
    """Combine a user question and approved schema text into one prompt."""
    if not question.strip():
        raise ValueError("Question must not be blank.")
    if not schema_text.strip():
        raise ValueError("Schema text must not be blank.")

    examples = """Question: List every customer ordered by name.
SQL: SELECT full_name FROM customers ORDER BY full_name

Question: How many customers are from Mumbai?
SQL: SELECT COUNT(*) FROM customers WHERE city = 'Mumbai'

Question: What is delivered revenue for each product?
SQL: SELECT p.product_name, COALESCE(SUM(o.quantity * p.unit_price), 0) AS revenue FROM products p LEFT JOIN orders o ON o.product_id = p.product_id AND o.status = 'delivered' GROUP BY p.product_name ORDER BY p.product_name"""

    return f"""Generate one PostgreSQL SELECT query that answers the question.
Use only tables and columns listed in the schema. Return SQL only.
Do not use INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, or multiple statements.

<examples>
{examples}
</examples>

<schema>
{schema_text.strip()}
</schema>

<question>
{question.strip()}
</question>
"""
