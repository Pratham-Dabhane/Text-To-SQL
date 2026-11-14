"""Build consistent text-to-SQL prompts."""

from text_to_sql.prompt_examples import format_examples


def build_sql_generation_prompt(question: str, schema_text: str) -> str:
    """Combine a user question and approved schema text into one prompt."""
    if not question.strip():
        raise ValueError("Question must not be blank.")
    if not schema_text.strip():
        raise ValueError("Schema text must not be blank.")

    examples = format_examples()

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
Before writing SQL, verify every selected, filtered, grouped, and ordered column
belongs to the table or alias that supplies it. If a requested field is in another
table, join through the listed foreign-key relationship instead of inventing a
same-named column. For totals grouped by an entity name, select that name and
join the entity table before grouping or ordering by it.
For many-to-many questions, join through the bridge table using both listed
foreign keys before selecting or filtering the related entity.
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
