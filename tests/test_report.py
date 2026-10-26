"""Unit tests for report exports."""

import json
from src.report import generate_csv_report, generate_json_report, results_to_dataframe
from src.scorer import ResumeResult


def test_reports_csv_and_json():
    """Verify DataFrame, CSV, and JSON generation."""
    res1 = ResumeResult(
        filename="cand1.pdf",
        final_score=85.5,
        semantic_score=80.0,
        skill_score=90.0,
        experience_section_score=85.0,
        lexical_score=75.0,
        matched_skills=["Docker", "Python"],
        missing_skills=["AWS"],
        extra_skills=["Git"],
        section_scores={"skills": 85.0},
        suggestions=["Add AWS example."],
    )
    res2 = ResumeResult(
        filename="cand2.docx",
        final_score=62.0,
        semantic_score=60.0,
        skill_score=None,  # No skills in JD
        experience_section_score=55.0,
        lexical_score=50.0,
        matched_skills=[],
        missing_skills=[],
        extra_skills=["Excel"],
        section_scores={},
        suggestions=[],
    )

    results = [res1, res2]

    # DataFrame
    df = results_to_dataframe(results)
    assert len(df) == 2
    assert "Rank" in df.columns
    assert "Candidate File" in df.columns
    assert df.iloc[0]["Rank"] == 1
    assert df.iloc[1]["Skill Match (%)"] == "N/A"

    # CSV
    csv_str = generate_csv_report(results)
    assert "Candidate File" in csv_str
    assert "cand1.pdf" in csv_str
    assert "cand2.docx" in csv_str

    # JSON
    json_str = generate_json_report(results)
    parsed = json.loads(json_str)
    assert len(parsed) == 2
    assert parsed[0]["filename"] == "cand1.pdf"
    assert parsed[0]["matched_skills"] == ["Docker", "Python"]
    assert parsed[1]["skill_score"] is None
