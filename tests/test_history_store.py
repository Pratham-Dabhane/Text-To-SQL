from text_to_sql.history_store import HistoryStore


def test_history_survives_new_store_instance(tmp_path):
    path = tmp_path / "history.sqlite3"
    first = HistoryStore(path)
    first.add("q1", "List customers", {"query_id": "q1", "action": "clarify"})
    first.add_feedback("q1", "correct")

    second = HistoryStore(path)
    assert second.list() == [
        {
            "question": "List customers",
            "query_id": "q1",
            "action": "clarify",
            "feedback": "correct",
        }
    ]
