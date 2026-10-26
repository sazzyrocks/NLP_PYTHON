"""Resume section parser detecting common headings via regex."""

import re
from typing import Dict, List, Optional, Tuple

SECTION_HEADING_PATTERNS: Dict[str, List[str]] = {
    "summary": [
        r"^(?:professional\s+)?summary",
        r"^career\s+(?:summary|objective)",
        r"^objective",
        r"^profile",
        r"^about(?:\s+me)?",
        r"^executive\s+summary",
    ],
    "skills": [
        r"^technical\s+skills",
        r"^skills(?:\s*(&|and)\s*(?:tools|abilities|competencies|expertise))?",
        r"^core\s+competencies",
        r"^technologies",
        r"^key\s+skills",
        r"^areas\s+of\s+expertise",
        r"^tools(?:\s*(&|and)\s*technologies)?",
    ],
    "experience": [
        r"^work\s+experience",
        r"^professional\s+experience",
        r"^experience",
        r"^employment\s+history",
        r"^career\s+history",
        r"^work\s+history",
        r"^relevant\s+experience",
        r"^internships?",
    ],
    "projects": [
        r"^(?:academic|personal|key|featured|technical)\s+projects",
        r"^projects",
    ],
    "education": [
        r"^education",
        r"^academic\s+(?:background|qualifications|history)",
        r"^education\s*(&|and)\s*training",
        r"^qualifications",
    ],
    "certifications": [
        r"^certifications?",
        r"^certificates?",
        r"^(?:licenses?|courses?)\s*(&|and)\s*certifications?",
    ],
}


def _match_heading(line: str) -> Optional[str]:
    """Check if a line matches any known section heading.

    A line is considered a heading candidate if:
    - It is relatively short (< 50 characters)
    - It matches one of the known section patterns (case-insensitive)

    Args:
        line: Raw line of text.

    Returns:
        Canonical section name if matched, else None.
    """
    clean_line = line.strip().lower()
    # Strip trailing punctuation often found on headings like colons, dashes, pipes
    clean_line = re.sub(r"[:\-\|\#\*\_\=\.\>\~]+$", "", clean_line).strip()
    clean_line = re.sub(r"^[:\-\|\#\*\_\=\.\>\~]+", "", clean_line).strip()

    if not clean_line or len(clean_line) > 50:
        return None

    # Line must have 1-6 words to be a heading
    words = clean_line.split()
    if not (1 <= len(words) <= 6):
        return None

    for section_name, patterns in SECTION_HEADING_PATTERNS.items():
        for pat in patterns:
            if re.fullmatch(pat, clean_line) or re.match(pat + r"\s*$", clean_line):
                return section_name

    return None


def parse_sections(text: str) -> Dict[str, str]:
    """Parse resume text into standard sections.

    Standard sections:
    - 'summary'
    - 'skills'
    - 'experience'
    - 'projects'
    - 'education'
    - 'certifications'

    Rules:
    - Text before the first recognized heading is mapped to 'summary'.
    - If no headings are recognized, the full text is returned under {'full_text': text}.
    - Consecutive sections of the same type are joined cleanly.

    Args:
        text: Raw or preprocessed resume text.

    Returns:
        Dictionary mapping section name to its extracted text content.
    """
    if not text or not text.strip():
        return {"full_text": ""}

    lines = [line.strip() for line in text.splitlines()]

    # Collect section boundaries
    detected_sections: List[Tuple[Optional[str], List[str]]] = []
    current_section: Optional[str] = None
    current_lines: List[str] = []

    for line in lines:
        if not line:
            continue

        matched_section = _match_heading(line)
        if matched_section:
            # We hit a new section heading
            if current_section is not None or current_lines:
                detected_sections.append((current_section, current_lines))
            current_section = matched_section
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines or current_section is not None:
        detected_sections.append((current_section, current_lines))

    # If no heading was ever matched, return everything under "full_text"
    if all(sec is None for sec, _ in detected_sections):
        return {"full_text": "\n".join(lines).strip()}

    # Consolidate sections into a dict
    sections_dict: Dict[str, List[str]] = {}
    for sec, sec_lines in detected_sections:
        content = "\n".join(sec_lines).strip()
        if not content:
            continue

        target_sec = sec if sec is not None else "summary"
        if target_sec not in sections_dict:
            sections_dict[target_sec] = []
        sections_dict[target_sec].append(content)

    return {k: "\n\n".join(v).strip() for k, v in sections_dict.items() if v}
