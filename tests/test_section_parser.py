"""Unit tests for resume section parser."""

from src.section_parser import parse_sections


def test_parse_sections_standard(sample_strong_resume_text):
    """Verify detection of standard resume sections."""
    sections = parse_sections(sample_strong_resume_text)

    assert "summary" in sections
    assert "skills" in sections
    assert "experience" in sections
    assert "projects" in sections
    assert "education" in sections
    assert "certifications" in sections

    assert "Senior Software Engineer" in sections["summary"]
    assert "FastAPI, Django" in sections["skills"]
    assert "CloudTech Corp" in sections["experience"]
    assert "ML Recommendation Engine" in sections["projects"]
    assert "Computer Science" in sections["education"]
    assert "Solutions Architect" in sections["certifications"]


def test_parse_sections_text_before_first_heading():
    """Verify unheaded text before the first section heading is classified as summary."""
    raw = (
        "Jane Developer\n"
        "Passionate full-stack developer with 5 years experience.\n\n"
        "Technical Skills\n"
        "Python, React, Docker\n\n"
        "Education\n"
        "B.S. Software Engineering"
    )
    sections = parse_sections(raw)
    assert "summary" in sections
    assert "Passionate full-stack developer" in sections["summary"]
    assert "skills" in sections
    assert "education" in sections


def test_parse_sections_no_headings_fallback():
    """Verify resume with no recognized headings maps everything to full_text."""
    raw = "Just a raw paragraph of developer bio with no section headings anywhere."
    sections = parse_sections(raw)
    assert "full_text" in sections
    assert sections["full_text"] == raw


def test_parse_sections_with_colons_and_dividers():
    """Verify headings followed by punctuation like colons, dashes, or pipes are recognized."""
    raw = (
        "PROFESSIONAL SUMMARY:\n"
        "Dedicated engineer.\n\n"
        "WORK EXPERIENCE ---\n"
        "Software Engineer at Acme.\n\n"
        "CORE COMPETENCIES |\n"
        "Python, SQL, Linux"
    )
    sections = parse_sections(raw)
    assert "summary" in sections
    assert "experience" in sections
    assert "skills" in sections
    assert "Dedicated engineer." in sections["summary"]
    assert "Software Engineer at Acme." in sections["experience"]
    assert "Python, SQL, Linux" in sections["skills"]


def test_parse_sections_empty():
    """Verify empty string returns empty full_text dict."""
    sections = parse_sections("")
    assert sections == {"full_text": ""}

    sections_ws = parse_sections("   \n\t  ")
    assert sections_ws == {"full_text": ""}
