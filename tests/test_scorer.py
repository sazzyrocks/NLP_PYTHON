"""Unit tests for scoring engine."""

import pytest

from src.scorer import (
    WEIGHTS,
    calculate_final_score,
    calculate_skill_breakdown,
    compute_lexical_score,
    score_resume,
)


def test_weights_dict_sum():
    """Verify default weights sum to 1.0."""
    total = sum(WEIGHTS.values())
    assert pytest.approx(total, 0.001) == 1.0


def test_calculate_skill_breakdown_full_match():
    """Verify 100% skill match score."""
    resume_skills = ["FastAPI", "PostgreSQL", "Python"]
    jd_skills = ["Python", "FastAPI", "PostgreSQL"]
    score, matched, missing, extra = calculate_skill_breakdown(resume_skills, jd_skills)

    assert score == 100.0
    assert matched == ["FastAPI", "PostgreSQL", "Python"]
    assert missing == []
    assert extra == []


def test_calculate_skill_breakdown_partial_and_extra():
    """Verify partial match and extra skill detection."""
    resume_skills = ["Docker", "Python", "React"]
    jd_skills = ["Docker", "Kubernetes", "Python"]
    score, matched, missing, extra = calculate_skill_breakdown(resume_skills, jd_skills)

    assert score == pytest.approx(66.67, 0.01)
    assert matched == ["Docker", "Python"]
    assert missing == ["Kubernetes"]
    assert extra == ["React"]


def test_calculate_skill_breakdown_empty_jd():
    """Verify that when JD has no skills, skill_score is None."""
    resume_skills = ["Python", "Docker"]
    jd_skills = []
    score, matched, missing, extra = calculate_skill_breakdown(resume_skills, jd_skills)

    assert score is None
    assert matched == []
    assert missing == []
    assert extra == ["Docker", "Python"]


def test_calculate_final_score_with_skill_score():
    """Verify weighted calculation when all components are active."""
    final = calculate_final_score(
        semantic_score=80.0,
        skill_score=90.0,
        experience_section_score=70.0,
        lexical_score=60.0,
    )
    # Expected: 80*0.35 + 90*0.40 + 70*0.15 + 60*0.10 = 28 + 36 + 10.5 + 6 = 80.5
    assert final == 80.5


def test_calculate_final_score_renormalization_without_skill_score():
    """Critical check: When JD has 0 skills, skill_score is None, remaining weights renormalize."""
    final = calculate_final_score(
        semantic_score=80.0,
        skill_score=None,
        experience_section_score=80.0,
        lexical_score=80.0,
    )
    # Since all active scores are 80.0, renormalized score MUST be 80.0, never penalized!
    assert final == 80.0


def test_calculate_final_score_zero_weights():
    """Verify zero total weights returns 0.0."""
    zero_weights = {k: 0.0 for k in WEIGHTS}
    final = calculate_final_score(80.0, 80.0, 80.0, 80.0, custom_weights=zero_weights)
    assert final == 0.0


def test_compute_lexical_score():
    """Test TF-IDF unigram+bigram lexical similarity."""
    t1 = "Senior Python engineer with experience in FastAPI and PostgreSQL databases."
    t2 = "Python engineer building web services with FastAPI and PostgreSQL."
    score = compute_lexical_score(t1, t2)
    assert score > 30.0

    unrelated = "Accountant managing quarterly tax filings and corporate ledgers."
    score_unrelated = compute_lexical_score(t1, unrelated)
    assert score_unrelated < score

    assert compute_lexical_score("", t1) == 0.0


def test_score_resume_end_to_end(mock_embedder):
    """Test full score_resume routine with sections and skills."""
    sections = {
        "summary": "Experienced engineer.",
        "skills": "Python, Docker, AWS",
        "experience": "Lead developer at tech firm building APIs.",
    }
    result = score_resume(
        filename="test_resume.pdf",
        resume_text="Experienced engineer in Python, Docker, AWS building APIs.",
        sections=sections,
        resume_skills=["AWS", "Docker", "Python"],
        jd_text="Looking for a Python and AWS cloud developer.",
        jd_skills=["AWS", "Python"],
        embedder=mock_embedder,
    )

    assert result.filename == "test_resume.pdf"
    assert 0.0 <= result.final_score <= 100.0
    assert result.skill_score == 100.0
    assert result.matched_skills == ["AWS", "Python"]
    assert result.missing_skills == []
    assert result.extra_skills == ["Docker"]
    assert "experience" in result.section_scores


def test_score_resume_missing_experience_section(mock_embedder):
    """Test resume lacking experience section sets experience_section_score to 0.0."""
    sections = {
        "summary": "Junior programmer.",
        "skills": "Python",
    }
    result = score_resume(
        filename="no_exp.pdf",
        resume_text="Junior programmer skilled in Python.",
        sections=sections,
        resume_skills=["Python"],
        jd_text="Need Python developer.",
        jd_skills=["Python"],
        embedder=mock_embedder,
    )
    assert result.experience_section_score == 0.0
