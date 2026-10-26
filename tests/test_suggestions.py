"""Unit tests for rule-based suggestions generator."""

from src.suggestions import generate_suggestions


def test_suggestions_missing_skills():
    """Verify missing skills trigger targeted advice."""
    missing = ["Kubernetes", "GraphQL", "Redis"]
    sections = {"skills": "Python, Docker", "experience": "Engineered systems for 500 users.", "summary": "Dev"}
    tips = generate_suggestions(
        missing_skills=missing,
        experience_section_score=75.0,
        sections=sections,
    )

    assert any("JD asks for Kubernetes" in t for t in tips)
    assert any("JD asks for GraphQL" in t for t in tips)
    assert any("JD asks for Redis" in t for t in tips)


def test_suggestions_many_missing_skills():
    """Verify remaining missing skills summary advice when count exceeds max."""
    missing = [f"Skill_{i}" for i in range(10)]
    sections = {"skills": "Python", "experience": "Saved 10 hours weekly.", "summary": "Dev"}
    tips = generate_suggestions(
        missing_skills=missing,
        experience_section_score=75.0,
        sections=sections,
        max_missing_skill_suggestions=5,
    )
    assert any("Review 5 additional JD skills" in t for t in tips)


def test_suggestions_low_experience_score():
    """Verify low experience score triggers rewrite advice."""
    sections = {"skills": "Python", "experience": "Worked on web projects for 100 clients.", "summary": "Dev"}
    tips = generate_suggestions(
        missing_skills=[],
        experience_section_score=40.0,  # Below default 50.0 threshold
        sections=sections,
    )
    assert "Rewrite experience bullets using wording from the JD." in tips


def test_suggestions_missing_skills_section():
    """Verify missing skills section triggers suggestion."""
    sections = {"summary": "Developer", "experience": "Built apps for 1000 users."}
    tips = generate_suggestions(
        missing_skills=[],
        experience_section_score=80.0,
        sections=sections,
    )
    assert "Add a dedicated Skills section." in tips


def test_suggestions_lack_of_quantified_metrics():
    """Verify unquantified experience bullets trigger metrics advice."""
    sections = {
        "summary": "Developer",
        "skills": "Python",
        "experience": "Worked on server tasks and assisted team members with bugs.",
    }
    tips = generate_suggestions(
        missing_skills=[],
        experience_section_score=80.0,
        sections=sections,
    )
    assert "Quantify impact (%, time saved, users)." in tips


def test_suggestions_quantified_metrics_present():
    """Verify quantified impact suppresses metrics advice."""
    sections = {
        "summary": "Developer",
        "skills": "Python",
        "experience": "Improved API latency by 35% and scaled system to 50,000 active users.",
    }
    tips = generate_suggestions(
        missing_skills=[],
        experience_section_score=80.0,
        sections=sections,
    )
    assert "Quantify impact (%, time saved, users)." not in tips


def test_suggestions_missing_summary():
    """Verify missing summary triggers professional summary advice."""
    sections = {
        "skills": "Python",
        "experience": "Built tools for 10 clients.",
    }
    tips = generate_suggestions(
        missing_skills=[],
        experience_section_score=80.0,
        sections=sections,
    )
    assert any("Professional Summary" in t for t in tips)
