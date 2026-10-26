"""Pipeline ranker orchestrating extraction, NLP parsing, scoring, and sorting."""

from typing import Dict, List, Optional, Tuple, Union
from src.embedder import SentenceEmbedder, get_embedder
from src.extractor import extract_text
from src.preprocessing import clean_text
from src.scorer import ResumeResult, score_resume
from src.section_parser import parse_sections
from src.skill_extractor import SkillExtractor, get_skill_extractor
from src.suggestions import generate_suggestions


def rank_resumes(
    jd_input: Union[str, bytes],
    resumes: List[Tuple[str, Union[bytes, str]]],
    jd_filename: Optional[str] = None,
    custom_weights: Optional[Dict[str, float]] = None,
    embedder: Optional[SentenceEmbedder] = None,
    skill_extractor: Optional[SkillExtractor] = None,
) -> Tuple[List[ResumeResult], List[Dict[str, str]]]:
    """Execute the end-to-end ranking pipeline on multiple resumes against a job description.

    Args:
        jd_input: Raw JD text (str) or binary document content (bytes).
        resumes: List of (filename, content) where content is raw bytes or text.
        jd_filename: Optional filename of JD if passed as bytes.
        custom_weights: Optional scoring weights override.
        embedder: Optional SentenceEmbedder instance.
        skill_extractor: Optional SkillExtractor instance.

    Returns:
        Tuple of:
          - Sorted list of ResumeResult objects (ordered by final_score descending).
          - List of error records for failed documents [{'filename': ..., 'error': ...}].
    """
    if embedder is None:
        embedder = get_embedder()
    if skill_extractor is None:
        skill_extractor = get_skill_extractor()

    # 1. Process Job Description
    if isinstance(jd_input, bytes):
        fname = jd_filename or "job_description.pdf"
        raw_jd_text = extract_text(fname, jd_input)
    else:
        raw_jd_text = str(jd_input)

    cleaned_jd = clean_text(raw_jd_text)
    jd_skills = skill_extractor.extract_skills(cleaned_jd)

    results: List[ResumeResult] = []
    errors: List[Dict[str, str]] = []

    # 2. Process each resume
    for filename, content in resumes:
        try:
            if isinstance(content, bytes):
                raw_resume_text = extract_text(filename, content)
            else:
                raw_resume_text = str(content)

            cleaned_resume = clean_text(raw_resume_text)
            sections = parse_sections(raw_resume_text)
            resume_skills = skill_extractor.extract_skills(cleaned_resume)

            res = score_resume(
                filename=filename,
                resume_text=cleaned_resume,
                sections=sections,
                resume_skills=resume_skills,
                jd_text=cleaned_jd,
                jd_skills=jd_skills,
                embedder=embedder,
                custom_weights=custom_weights,
            )

            res.suggestions = generate_suggestions(
                missing_skills=res.missing_skills,
                experience_section_score=res.experience_section_score,
                sections=sections,
                full_text=cleaned_resume,
            )

            results.append(res)
        except Exception as exc:
            errors.append({"filename": filename, "error": str(exc)})

    # 3. Sort descending by final_score
    results.sort(key=lambda r: r.final_score, reverse=True)

    return results, errors
