"""Convert inspected database metadata into readable prompt context."""

from __future__ import annotations

from typing import Any


def format_schema_for_prompt(schema: dict[str, Any]) -> str:
    """Format schema metadata as stable, readable plain text.

    The input is the dictionary returned by ``inspect_schema``. Sorting table
    names makes the result deterministic, which helps tests and makes later
    prompts easier to compare while debugging.
    """
    tables = schema.get("tables")
    if not isinstance(tables, dict) or not tables:
        raise ValueError("Schema must contain a non-empty 'tables' dictionary.")

    sections: list[str] = []
    for table_name in sorted(tables):
        table = tables[table_name]
        columns = table.get("columns")
        primary_key = table.get("primary_key")
        foreign_keys = table.get("foreign_keys")

        if not isinstance(columns, list):
            raise ValueError(f"Table '{table_name}' must contain a 'columns' list.")
        if not isinstance(primary_key, list):
            raise ValueError(f"Table '{table_name}' must contain a 'primary_key' list.")
        if not isinstance(foreign_keys, list):
            raise ValueError(f"Table '{table_name}' must contain a 'foreign_keys' list.")

        relationship_by_column = {
            foreign_key["columns"][0]: (
                f"{foreign_key['referred_table']}."
                f"{foreign_key['referred_columns'][0]}"
            )
            for foreign_key in foreign_keys
            if len(foreign_key["columns"]) == 1
            and len(foreign_key["referred_columns"]) == 1
        }

        lines = [f"TABLE {table_name}"]
        for column in columns:
            line = f"  {column['name']} {column['type']}"
            if not column["nullable"]:
                line += " NOT NULL"
            if column["name"] in primary_key:
                line += " PRIMARY KEY"
            if column["name"] in relationship_by_column:
                line += f" REFERENCES {relationship_by_column[column['name']]}"
            lines.append(line)

        sections.append("\n".join(lines))

    return "\n\n".join(sections)
