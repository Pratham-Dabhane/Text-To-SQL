from text_to_sql.prompt_examples import SQL_EXAMPLES, format_examples


def test_examples_are_question_sql_pairs():
    assert len(SQL_EXAMPLES) > 0
    assert all(question and sql.startswith("SELECT") for question, sql in SQL_EXAMPLES)


def test_example_formatter_preserves_question_and_sql_labels():
    text = format_examples()

    assert text.startswith("Question: ")
    assert "\nSQL: SELECT" in text
