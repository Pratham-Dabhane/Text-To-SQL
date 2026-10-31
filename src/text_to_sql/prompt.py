"""Build consistent text-to-SQL prompts."""


def build_sql_generation_prompt(question: str, schema_text: str) -> str:
    """Combine a user question and approved schema text into one prompt."""
    if not question.strip():
        raise ValueError("Question must not be blank.")
    if not schema_text.strip():
        raise ValueError("Schema text must not be blank.")

    return f"""Generate one PostgreSQL SELECT query that answers the question.
Use only tables and columns listed in the schema. Return SQL only.
Do not use INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, or multiple statements.

<schema>
{schema_text.strip()}
</schema>

<question>
{question.strip()}
</question>
"""
