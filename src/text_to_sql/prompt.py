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
SQL: SELECT p.product_name, COALESCE(SUM(o.quantity * p.unit_price), 0) AS revenue FROM products p LEFT JOIN orders o ON o.product_id = p.product_id AND o.status = 'delivered' GROUP BY p.product_name ORDER BY p.product_name

Question: For each customer, return the customer's name and count of orders.
SQL: SELECT c.full_name, COUNT(o.order_id) AS order_count FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id GROUP BY c.full_name ORDER BY c.full_name

Question: What is the most expensive product? Return its name and price.
SQL: SELECT product_name, unit_price FROM products ORDER BY unit_price DESC LIMIT 1

Question: What is the total quantity ordered for Stationery products?
SQL: SELECT SUM(o.quantity) FROM orders o JOIN products p ON p.product_id = o.product_id WHERE p.category = 'Stationery'"""

    return f"""Generate one PostgreSQL SELECT query that answers the question.
Select exactly the fields requested. Distinguish product_name from category:
category is a products column and values such as 'Stationery' belong in
filters on products.category. Use the requested aggregate and preserve the
requested level of detail. Return SQL only.
Do not add LIMIT unless the question asks for one/top/bottom result or a row limit.
Use only tables and columns listed in the schema.
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
