from text_to_sql.generation import generate_validated_sql


class FakeClient:
    def generate(self, prompt: str) -> str:
        self.prompt = prompt
        return "```sql\nSELECT full_name FROM customers\n```"


def test_generation_builds_prompt_and_validates_sql():
    client = FakeClient()

    generated, validated = generate_validated_sql(
        "List customers.", "TABLE customers\n  full_name TEXT", client
    )

    assert "List customers." in client.prompt
    assert generated.startswith("```sql")
    assert validated == "SELECT full_name FROM customers"
