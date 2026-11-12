"""Smoke tests and Streamlit AppTest for the web UI."""

import pytest

st = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402
from app import render_skill_badges  # noqa: E402


def test_render_skill_badges():
    """Verify HTML skill pill badge generator."""
    html_green = render_skill_badges(["Python", "AWS"], "green")
    assert "badge-green" in html_green
    assert "Python" in html_green
    assert "AWS" in html_green

    html_empty = render_skill_badges([], "red")
    assert "None detected" in html_empty


def test_app_smoke_test():
    """Smoke test app initialization with Streamlit AppTest."""
    at = AppTest.from_file("../app.py", default_timeout=30)
    at.run()

    # App should initialize cleanly without uncaught exceptions
    assert not at.exception
    # Check that main elements exist
    assert len(at.sidebar.radio) > 0
    assert len(at.sidebar.text_area) > 0


def test_app_demo_run():
    """Verify demo candidate evaluation renders properly."""
    at = AppTest.from_file("../app.py", default_timeout=30)
    at.run()
    assert not at.exception

    # Click preset button
    at.sidebar.button[0].click().run()
    assert not at.exception

    # Click demo comparison button
    demo_btn = [b for b in at.button if "Run Demo" in b.label][0]
    demo_btn.click().run()
    assert not at.exception
