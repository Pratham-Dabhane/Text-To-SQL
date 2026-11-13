"""Small Streamlit client for the local Text-to-SQL API."""

from __future__ import annotations

import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

st.set_page_config(page_title="Safe Text-to-SQL", layout="wide")
st.title("Safe Text-to-SQL")
st.caption("Questions are generated and executed through the local guarded API.")

question = st.text_input("Ask a question", placeholder="List customers in Mumbai.")
if st.button("Run query", type="primary") and question.strip():
    try:
        response = requests.post(
            f"{API_URL}/v1/query", json={"question": question}, headers=HEADERS, timeout=120
        )
        response.raise_for_status()
        payload = response.json()
        if payload["action"] == "clarify":
            st.warning(payload["reason"])
            for option in payload.get("options", []):
                st.write(f"• {option}")
        elif payload["action"] == "executed":
            st.subheader("Generated SQL")
            st.code(payload["generated_sql"], language="sql")
            result = payload["result"]
            st.subheader(f"Results ({result['row_count']} rows)")
            st.dataframe(result["rows"], use_container_width=True)
            for warning in result["sanity"]["warnings"]:
                st.warning(warning)
            st.session_state["last_query_id"] = payload["query_id"]
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")

if st.session_state.get("last_query_id"):
    st.caption("Was this result correct?")
    yes_col, no_col = st.columns(2)
    for column, label, value in ((yes_col, "Correct", True), (no_col, "Incorrect", False)):
        if column.button(label):
            try:
                feedback = requests.post(
                    f"{API_URL}/v1/feedback",
                    json={"query_id": st.session_state["last_query_id"], "is_correct": value},
                    headers=HEADERS, timeout=10,
                )
                feedback.raise_for_status()
                st.success("Feedback saved.")
            except requests.RequestException as exc:
                st.error(f"Could not save feedback: {exc}")

if st.checkbox("Show query history"):
    try:
        history = requests.get(f"{API_URL}/v1/history", headers=HEADERS, timeout=10).json()
        st.json(history)
    except requests.RequestException as exc:
        st.error(f"Could not load history: {exc}")
