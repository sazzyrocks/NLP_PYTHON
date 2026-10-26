"""Unit tests for the end-to-end ranker pipeline."""

from src.ranker import rank_resumes
from src.skill_extractor import get_skill_extractor


def test_rank_resumes_ordering(
    sample_jd_text,
    sample_strong_resume_text,
    sample_weak_resume_text,
    mock_embedder,
):
    """Verify strong resume ranks above weak resume."""
    skill_ext = get_skill_extractor()

    resumes = [
        ("weak_candidate.txt", sample_weak_resume_text),
        ("strong_candidate.txt", sample_strong_resume_text),
    ]

    results, errors = rank_resumes(
        jd_input=sample_jd_text,
        resumes=resumes,
        embedder=mock_embedder,
        skill_extractor=skill_ext,
    )

    assert len(errors) == 0
    assert len(results) == 2

    # Check descending order
    assert results[0].final_score >= results[1].final_score
    assert results[0].filename == "strong_candidate.txt"
    assert results[1].filename == "weak_candidate.txt"

    # Strong candidate should have high skill match
    assert len(results[0].matched_skills) > len(results[1].matched_skills)


def test_rank_resumes_with_bytes_and_error_handling(
    sample_jd_text,
    synthetic_pdf_bytes,
    mock_embedder,
):
    """Verify ranker handles bytes inputs and isolates errors for corrupt files."""
    skill_ext = get_skill_extractor()

    resumes = [
        ("valid_candidate.pdf", synthetic_pdf_bytes),
        ("corrupted.pdf", b"corrupted bytes without valid pdf header"),
        ("unsupported.exe", b"binary executable"),
    ]

    results, errors = rank_resumes(
        jd_input=sample_jd_text,
        resumes=resumes,
        embedder=mock_embedder,
        skill_extractor=skill_ext,
    )

    assert len(results) == 1
    assert results[0].filename == "valid_candidate.pdf"

    assert len(errors) == 2
    error_filenames = [e["filename"] for e in errors]
    assert "corrupted.pdf" in error_filenames
    assert "unsupported.exe" in error_filenames


def test_rank_resumes_with_jd_bytes(
    synthetic_pdf_bytes,
    sample_strong_resume_text,
    mock_embedder,
):
    """Verify ranker can process Job Description supplied as document bytes."""
    skill_ext = get_skill_extractor()

    resumes = [
        ("strong.txt", sample_strong_resume_text),
    ]

    results, errors = rank_resumes(
        jd_input=synthetic_pdf_bytes,
        jd_filename="jd.pdf",
        resumes=resumes,
        embedder=mock_embedder,
        skill_extractor=skill_ext,
    )

    assert len(errors) == 0
    assert len(results) == 1
    assert results[0].filename == "strong.txt"
