"""Scoring engine combining semantic embeddings, skill matching, experience relevance, and lexical TF-IDF."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.embedder import SentenceEmbedder, get_embedder

WEIGHTS: Dict[str, float] = {
    "semantic_score": 0.35,
    "skill_score": 0.40,
    "experience_section_score": 0.15,
    "lexical_score": 0.10,
}


@dataclass
class ResumeResult:
    """Comprehensive evaluation result for a single candidate resume."""

    filename: str
    final_score: float
    semantic_score: float
    skill_score: Optional[float]
    experience_section_score: float
    lexical_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    extra_skills: List[str]
    section_scores: Dict[str, float] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    raw_text: Optional[str] = None


def compute_lexical_score(resume_text: str, jd_text: str) -> float:
    """Compute lexical overlap score (0-100) using TF-IDF with unigrams and bigrams.

    Args:
        resume_text: Cleaned resume text.
        jd_text: Cleaned job description text.

    Returns:
        Cosine similarity score scaled to 0-100.
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words="english",
        )
        tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        score = max(0.0, min(1.0, float(sim))) * 100.0
        return round(score, 2)
    except Exception:
        return 0.0


def calculate_skill_breakdown(
    resume_skills: List[str], jd_skills: List[str]
) -> tuple[Optional[float], List[str], List[str], List[str]]:
    """Determine matched, missing, and extra skills, along with skill match score.

    Args:
        resume_skills: Skills extracted from candidate resume.
        jd_skills: Skills extracted from job description.

    Returns:
        Tuple of (skill_score, matched_skills, missing_skills, extra_skills).
        skill_score is None if jd_skills is empty.
    """
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = sorted(list(resume_set & jd_set))
    missing = sorted(list(jd_set - resume_set))
    extra = sorted(list(resume_set - jd_set))

    if not jd_set:
        skill_score = None
    else:
        skill_score = round((len(matched) / len(jd_set)) * 100.0, 2)

    return skill_score, matched, missing, extra


def calculate_final_score(
    semantic_score: float,
    skill_score: Optional[float],
    experience_section_score: float,
    lexical_score: float,
    custom_weights: Optional[Dict[str, float]] = None,
) -> float:
    """Compute weighted composite final score (0-100).

    If skill_score is None (e.g. JD has no recognized skills),
    skill_score is omitted and the remaining weights are renormalized to sum to 1.0.

    Args:
        semantic_score: Embedding similarity score (0-100).
        skill_score: Skill match percentage (0-100) or None.
        experience_section_score: Experience/Projects semantic score (0-100).
        lexical_score: TF-IDF cosine score (0-100).
        custom_weights: Optional override for default WEIGHTS.

    Returns:
        Weighted score bounded between 0.0 and 100.0, rounded to 2 decimals.
    """
    weights = dict(custom_weights) if custom_weights else dict(WEIGHTS)

    sub_scores: Dict[str, Optional[float]] = {
        "semantic_score": semantic_score,
        "skill_score": skill_score,
        "experience_section_score": experience_section_score,
        "lexical_score": lexical_score,
    }

    # Determine active components
    active_weights: Dict[str, float] = {}
    for component, weight in weights.items():
        if sub_scores.get(component) is not None:
            active_weights[component] = max(0.0, float(weight))

    total_active_weight = sum(active_weights.values())

    if total_active_weight == 0.0:
        return 0.0

    # Renormalize active weights to sum to 1.0
    normalized_weights = {
        comp: w / total_active_weight for comp, w in active_weights.items()
    }

    final_score = sum(
        sub_scores[comp] * normalized_weights[comp]
        for comp in normalized_weights
    )

    clipped = max(0.0, min(100.0, float(final_score)))
    return round(clipped, 2)


def score_resume(
    filename: str,
    resume_text: str,
    sections: Dict[str, str],
    resume_skills: List[str],
    jd_text: str,
    jd_skills: List[str],
    embedder: Optional[SentenceEmbedder] = None,
    custom_weights: Optional[Dict[str, float]] = None,
) -> ResumeResult:
    """Evaluate and score a single resume against a job description.

    Args:
        filename: Name of the resume file.
        resume_text: Cleaned full resume text.
        sections: Dictionary of parsed resume sections.
        resume_skills: Extracted skills from resume.
        jd_text: Cleaned job description text.
        jd_skills: Extracted skills from job description.
        embedder: SentenceEmbedder instance (defaults to singleton).
        custom_weights: Optional custom weight mapping.

    Returns:
        ResumeResult containing comprehensive scores and skill analysis.
    """
    if embedder is None:
        embedder = get_embedder()

    # 1. Semantic Score (Full resume vs JD using chunk-max similarity)
    semantic_score = embedder.compute_max_chunk_similarity(
        long_text=resume_text,
        reference_text=jd_text,
        chunk_size=200,
    )

    # 2. Skill Score & Skill Breakdown
    skill_score, matched_skills, missing_skills, extra_skills = calculate_skill_breakdown(
        resume_skills=resume_skills, jd_skills=jd_skills
    )

    # 3. Experience Section Score
    # Combine 'experience' and 'projects' sections if available
    exp_parts = []
    if "experience" in sections and sections["experience"].strip():
        exp_parts.append(sections["experience"].strip())
    if "projects" in sections and sections["projects"].strip():
        exp_parts.append(sections["projects"].strip())

    if exp_parts:
        exp_combined = "\n\n".join(exp_parts)
        experience_section_score = embedder.compute_max_chunk_similarity(
            long_text=exp_combined,
            reference_text=jd_text,
            chunk_size=200,
        )
    else:
        # If no explicit experience/projects section, fallback to 0.0 to signal gap
        experience_section_score = 0.0

    # Section-wise breakdown scores
    section_scores: Dict[str, float] = {}
    for sec_name, sec_text in sections.items():
        if sec_text.strip():
            section_scores[sec_name] = embedder.compute_max_chunk_similarity(
                long_text=sec_text,
                reference_text=jd_text,
                chunk_size=150,
            )

    # 4. Lexical Score (TF-IDF unigram + bigram cosine)
    lexical_score = compute_lexical_score(resume_text=resume_text, jd_text=jd_text)

    # 5. Composite Final Score
    final_score = calculate_final_score(
        semantic_score=semantic_score,
        skill_score=skill_score,
        experience_section_score=experience_section_score,
        lexical_score=lexical_score,
        custom_weights=custom_weights,
    )

    return ResumeResult(
        filename=filename,
        final_score=final_score,
        semantic_score=semantic_score,
        skill_score=skill_score,
        experience_section_score=experience_section_score,
        lexical_score=lexical_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        extra_skills=extra_skills,
        section_scores=section_scores,
        suggestions=[],
        raw_text=resume_text,
    )
