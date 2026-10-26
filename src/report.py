"""Report generation module for CSV and JSON exports."""

import json
from typing import Any, Dict, List
import pandas as pd

from src.scorer import ResumeResult


def results_to_dataframe(results: List[ResumeResult]) -> pd.DataFrame:
    """Convert a list of ResumeResults into a pandas DataFrame suitable for tabular display.

    Args:
        results: Ranked list of ResumeResult objects.

    Returns:
        DataFrame with formatted columns.
    """
    rows = []
    for rank, res in enumerate(results, start=1):
        rows.append(
            {
                "Rank": rank,
                "Candidate File": res.filename,
                "Final Score": res.final_score,
                "Skill Match (%)": f"{res.skill_score:.1f}%" if res.skill_score is not None else "N/A",
                "Semantic Score": res.semantic_score,
                "Experience Score": res.experience_section_score,
                "Lexical Score": res.lexical_score,
                "Matched Skills Count": len(res.matched_skills),
                "Missing Skills Count": len(res.missing_skills),
                "Matched Skills": ", ".join(res.matched_skills),
                "Missing Skills": ", ".join(res.missing_skills),
            }
        )

    return pd.DataFrame(rows)


def generate_csv_report(results: List[ResumeResult]) -> str:
    """Export ranked resume results as a CSV formatted string.

    Args:
        results: Ranked list of ResumeResult objects.

    Returns:
        CSV string content.
    """
    df = results_to_dataframe(results)
    return df.to_csv(index=False)


def generate_json_report(results: List[ResumeResult], indent: int = 2) -> str:
    """Export ranked resume results as a structured JSON string.

    Args:
        results: Ranked list of ResumeResult objects.
        indent: JSON indentation spaces.

    Returns:
        JSON string content.
    """
    payload: List[Dict[str, Any]] = []
    for rank, res in enumerate(results, start=1):
        payload.append(
            {
                "rank": rank,
                "filename": res.filename,
                "final_score": res.final_score,
                "skill_score": res.skill_score,
                "semantic_score": res.semantic_score,
                "experience_section_score": res.experience_section_score,
                "lexical_score": res.lexical_score,
                "matched_skills": res.matched_skills,
                "missing_skills": res.missing_skills,
                "extra_skills": res.extra_skills,
                "section_scores": res.section_scores,
                "suggestions": res.suggestions,
            }
        )

    return json.dumps(payload, indent=indent, ensure_ascii=False)
