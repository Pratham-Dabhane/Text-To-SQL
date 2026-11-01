"""Basic check that the Streamlit entry point exists."""

from pathlib import Path


def test_streamlit_entry_point_exists():
    assert (Path(__file__).parents[1] / "ui" / "streamlit_app.py").exists()
