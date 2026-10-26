"""Smoke tests and Streamlit AppTest for the web UI."""

from streamlit.testing.v1 import AppTest

from app import render_skill_badges


def test_render_skill_badges():
    """Verify HTML skill pill badge generator."""
    html_green = render_skill_badges(["Python", "AWS"], "green")
    assert "badge-green" in html_green
    assert "Python" in html_green
    assert "AWS" in html_green

    html_empty = render_skill_badges([], "red")
    assert "None detected" in html_empty


def test_app_smoke_test(monkeypatch):
    """Smoke test app initialization with Streamlit AppTest."""
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()

    # App should initialize cleanly without uncaught exceptions
    assert not at.exception
    # Check that main elements exist
    assert len(at.sidebar.radio) > 0
    assert len(at.sidebar.text_area) > 0
