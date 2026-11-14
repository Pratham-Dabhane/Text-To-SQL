"""Curated regression guidance used by the SQL generation prompt."""

from __future__ import annotations


SQL_EXAMPLES = (
    ("List every customer ordered by name.", "SELECT full_name FROM customers ORDER BY full_name"),
    ("How many customers are from Mumbai?", "SELECT COUNT(*) FROM customers WHERE city = 'Mumbai'"),
    ("What is delivered revenue for each product?", "SELECT p.product_name, COALESCE(SUM(o.quantity * p.unit_price), 0) AS revenue FROM products p LEFT JOIN orders o ON o.product_id = p.product_id AND o.status = 'delivered' GROUP BY p.product_name ORDER BY p.product_name"),
    ("For each customer, return the customer's name and count of orders.", "SELECT c.full_name, COUNT(o.order_id) AS order_count FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id GROUP BY c.full_name ORDER BY c.full_name"),
    ("What is the most expensive product? Return its name and price.", "SELECT product_name, unit_price FROM products ORDER BY unit_price DESC LIMIT 1"),
    ("What is the total quantity ordered for Stationery products?", "SELECT SUM(o.quantity) FROM orders o JOIN products p ON p.product_id = o.product_id WHERE p.category = 'Stationery'"),
    ("What is the delivered revenue from Notebook orders?", "SELECT SUM(o.quantity * p.unit_price) FROM orders o JOIN products p ON p.product_id = o.product_id WHERE p.product_name = 'Notebook' AND o.status = 'delivered'"),
    ("What is the average quantity per delivered order?", "SELECT AVG(quantity) FROM orders WHERE status = 'delivered'"),
    ("How many customers are in each city?", "SELECT city, COUNT(*) FROM customers GROUP BY city ORDER BY city"),
    ("For each customer with a pending order, return the name and pending order count.", "SELECT c.full_name, COUNT(o.order_id) FROM customers c JOIN orders o ON o.customer_id = c.customer_id WHERE o.status = 'pending' GROUP BY c.full_name ORDER BY c.full_name"),
    ("Count orders for each status, ordered by status.", "SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status"),
    ("List names of customers whose orders were placed before July 5, 2025.", "SELECT DISTINCT c.full_name FROM customers c JOIN orders o ON o.customer_id = c.customer_id WHERE o.ordered_at < DATE '2025-07-05' ORDER BY c.full_name"),
    ("Return every product priced below 20 with its name and price, cheapest first.", "SELECT product_name, unit_price FROM products WHERE unit_price < 20 ORDER BY unit_price"),
)


def format_examples() -> str:
    """Format examples in the text layout expected by the local model."""
    return "\n\n".join(
        f"Question: {question}\nSQL: {sql}" for question, sql in SQL_EXAMPLES
    )
