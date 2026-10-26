"""Rule-based resume tailoring suggestions generator."""

import re
from typing import Dict, List, Optional

# Pattern to detect quantified metrics (percentages, numbers, multipliers, monetary values)
METRIC_REGEX = (
    r"(\b\d+(?:\.\d+)?%\b|\$\s*\d+(?:,\d+)*(?:\.\d+)?|"
    r"\b\d+\s*(?:x|k|m|million|billion|users|clients|requests|ms|hours|days|percent)\b|\b\d+\b)"
)
METRIC_PATTERN = re.compile(METRIC_REGEX, re.IGNORECASE)


def generate_suggestions(
    missing_skills: List[str],
    experience_section_score: float,
    sections: Dict[str, str],
    experience_threshold: float = 50.0,
    max_missing_skill_suggestions: int = 5,
    full_text: Optional[str] = None,
) -> List[str]:
    """Generate explainable, rule-based resume optimization tips.

    Rules:
    1. Missing skills: For top missing JD skills, prompt candidate to add them with examples.
    2. Low experience score: Prompt rewriting experience bullets using JD phrasing.
    3. Missing skills section: Recommend adding a dedicated skills section.
    4. Lack of metrics/numbers in experience: Recommend quantifying impact (%, time saved, users).
    5. Missing summary section: Recommend a targeted summary.

    Args:
        missing_skills: List of skills requested by JD but absent in resume.
        experience_section_score: Experience relevance score (0-100).
        sections: Dictionary of parsed resume sections.
        experience_threshold: Score below which experience rewrite is suggested.
        max_missing_skill_suggestions: Limit on individual missing skill recommendations.
        full_text: Optional full resume text for fallback checking.

    Returns:
        List of actionable advice strings.
    """
    suggestions: List[str] = []

    # Rule 1: Missing skills
    for skill in missing_skills[:max_missing_skill_suggestions]:
        suggestions.append(
            f"JD asks for {skill} — add it if you've used it, with a concrete example."
        )

    if len(missing_skills) > max_missing_skill_suggestions:
        remaining_count = len(missing_skills) - max_missing_skill_suggestions
        suggestions.append(
            f"Review {remaining_count} additional JD skills you might possess and highlight them where relevant."
        )

    # Rule 2: Dedicated skills section
    if "skills" not in sections or not sections["skills"].strip():
        suggestions.append("Add a dedicated Skills section.")

    # Rule 3: Low experience section score
    if experience_section_score < experience_threshold:
        suggestions.append("Rewrite experience bullets using wording from the JD.")

    # Rule 4: Quantified impact in experience bullets
    exp_text = ""
    if "experience" in sections and sections["experience"].strip():
        exp_text += sections["experience"]
    if "projects" in sections and sections["projects"].strip():
        exp_text += " " + sections["projects"]

    if not exp_text.strip() and full_text:
        exp_text = full_text

    has_metrics = bool(METRIC_PATTERN.search(exp_text))
    if exp_text.strip() and not has_metrics:
        suggestions.append("Quantify impact (%, time saved, users).")

    # Rule 5: Professional Summary
    if "summary" not in sections or not sections["summary"].strip():
        suggestions.append(
            "Include a concise Professional Summary at the top tailored to the target role."
        )

    return suggestions
