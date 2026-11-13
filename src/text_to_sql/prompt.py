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
SQL: SELECT SUM(o.quantity) FROM orders o JOIN products p ON p.product_id = o.product_id WHERE p.category = 'Stationery'

Question: What is the delivered revenue from Notebook orders?
SQL: SELECT SUM(o.quantity * p.unit_price) FROM orders o JOIN products p ON p.product_id = o.product_id WHERE p.product_name = 'Notebook' AND o.status = 'delivered'

Question: What is the average quantity per delivered order?
SQL: SELECT AVG(quantity) FROM orders WHERE status = 'delivered'

Question: How many customers are in each city?
SQL: SELECT city, COUNT(*) FROM customers GROUP BY city ORDER BY city

Question: For each customer with a pending order, return the name and pending order count.
SQL: SELECT c.full_name, COUNT(o.order_id) FROM customers c JOIN orders o ON o.customer_id = c.customer_id WHERE o.status = 'pending' GROUP BY c.full_name ORDER BY c.full_name

Question: Count orders for each status, ordered by status.
SQL: SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status"""

    return f"""Generate one PostgreSQL SELECT query that answers the question.
Select exactly the fields requested. Distinguish product_name from category:
category is a products column and values such as 'Stationery' belong in
filters on products.category. Use the requested aggregate and preserve the
requested level of detail. Return SQL only.
Do not add LIMIT unless the question asks for one/top/bottom result or a row limit.
If the question says ordered, sorted, cheapest, lowest, highest, or newest, include
the matching ORDER BY clause. A cheapest, lowest, highest, or most expensive
question asking for one item also needs LIMIT 1. Preserve the exact filter concept: a product name filters
products.product_name, while a category filters products.category.
If the question asks for a value "for each" city, category, product, or customer,
return the grouping column and use GROUP BY; do not use only COUNT(DISTINCT ...).
When an order status is named, filter orders.status to that status.
For "with a pending order", exclude customers with zero matching orders. When
grouping, select the grouping column as well as the aggregate. A price range
filters products.unit_price, and "ordered before/after" refers to
orders.ordered_at; join customers through orders when customer names are needed.
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
