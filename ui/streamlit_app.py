"""Small Streamlit client for the local Text-to-SQL API."""

from __future__ import annotations

import requests
import streamlit as st


API_URL = "http://localhost:8000"

st.set_page_config(page_title="Safe Text-to-SQL", layout="wide")
st.title("Safe Text-to-SQL")
st.caption("Questions are generated and executed through the local guarded API.")

question = st.text_input("Ask a question", placeholder="List customers in Mumbai.")
if st.button("Run query", type="primary") and question.strip():
    try:
        response = requests.post(
            f"{API_URL}/v1/query", json={"question": question}, timeout=120
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
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")

if st.checkbox("Show query history"):
    try:
        history = requests.get(f"{API_URL}/v1/history", timeout=10).json()
        st.json(history)
    except requests.RequestException as exc:
        st.error(f"Could not load history: {exc}")
