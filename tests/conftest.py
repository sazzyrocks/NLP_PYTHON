"""Test fixtures and mock utilities for test suite."""

import io
from typing import List
import docx
import fitz
import numpy as np
import pytest

from src.embedder import SentenceEmbedder


@pytest.fixture
def sample_jd_text() -> str:
    """Standard Job Description containing recognized skills and requirements."""
    return (
        "We are looking for a Senior Backend Python Developer.\n"
        "Requirements:\n"
        "- 5+ years of experience with Python, FastAPI, and Django.\n"
        "- Strong understanding of PostgreSQL, Redis, and Docker.\n"
        "- Experience with AWS and CI/CD pipelines.\n"
        "- Familiarity with Machine Learning and REST API principles.\n"
        "- Excellent communication and problem solving skills."
    )


@pytest.fixture
def sample_jd_no_skills_text() -> str:
    """Job Description with generic text and zero recognizable technical skills."""
    return "Looking for an energetic, enthusiastic person who loves talking to people and walking in the park."


@pytest.fixture
def sample_strong_resume_text() -> str:
    """Resume strongly matching the sample JD."""
    return (
        "Jane Doe\n"
        "Professional Summary\n"
        "Senior Software Engineer specializing in scalable Python web services and cloud infrastructure.\n\n"
        "Technical Skills\n"
        "Languages: Python, SQL, Bash\n"
        "Frameworks: FastAPI, Django, Flask\n"
        "Databases: PostgreSQL, Redis\n"
        "DevOps & Cloud: Docker, Kubernetes, AWS, CI/CD, Linux\n"
        "Other: REST API, Machine Learning, Git\n\n"
        "Work Experience\n"
        "Lead Developer at CloudTech Corp (2020 - Present)\n"
        "- Designed and deployed high-throughput microservices using Python and FastAPI.\n"
        "- Architected PostgreSQL databases with Redis caching, reducing query latency by 45%.\n"
        "- Led automated CI/CD deployments using Docker and GitHub Actions on AWS.\n\n"
        "Academic Projects\n"
        "ML Recommendation Engine (2019)\n"
        "- Built a machine learning model using Python serving 10,000 active users.\n\n"
        "Education\n"
        "B.S. in Computer Science, State University\n\n"
        "Certifications\n"
        "AWS Certified Solutions Architect"
    )


@pytest.fixture
def sample_weak_resume_text() -> str:
    """Resume with low alignment to the sample JD."""
    return (
        "Bob Smith\n"
        "Summary\n"
        "Experienced accountant with a background in tax preparation and corporate bookkeeping.\n\n"
        "Skills\n"
        "Tax preparation, Bookkeeping, Microsoft Excel, Quickbooks, Financial Reporting\n\n"
        "Professional Experience\n"
        "Senior Accountant at Ledger Firm (2018 - Present)\n"
        "- Prepared quarterly tax returns and financial statements.\n"
        "- Managed payroll and vendor invoices.\n\n"
        "Education\n"
        "B.A. in Accounting"
    )


@pytest.fixture
def sample_unsectioned_resume_text() -> str:
    """Resume text without any standard section headings."""
    return (
        "John Developer. Enthusiastic programmer skilled in Python and C++. "
        "Worked on backend APIs and database queries. Loves building software."
    )


@pytest.fixture
def synthetic_pdf_bytes() -> bytes:
    """Generate in-memory valid PDF bytes containing extractable text."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        fitz.Point(50, 72),
        "John Doe\nSummary: Software engineer with Python and Docker experience.\nWork Experience:\n- Built REST APIs.",
    )
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def synthetic_image_pdf_bytes() -> bytes:
    """Generate in-memory PDF without extractable text layer (simulating scanned document)."""
    doc = fitz.open()
    doc.new_page()  # Blank page with zero text
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def synthetic_docx_bytes() -> bytes:
    """Generate in-memory valid DOCX bytes containing paragraphs and a table."""
    doc = docx.Document()
    doc.add_heading("Jane Developer", level=1)
    doc.add_paragraph("Summary: Experienced engineer in FastAPI and PostgreSQL.")
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Skill"
    table.cell(0, 1).text = "Level"
    table.cell(1, 0).text = "Python"
    table.cell(1, 1).text = "Expert"

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()


class MockSentenceTransformer:
    """Deterministic fake SentenceTransformer that does not require downloading weights."""

    def __init__(self, dim: int = 16):
        self.dim = dim

    def encode(
        self,
        texts: List[str],
        convert_to_numpy: bool = True,
        normalize_embeddings: bool = True,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]

        matrix = []
        for text in texts:
            # Deterministic pseudo-embedding from text hash
            val = float(abs(hash(text)) % 1000) + 1.0
            vec = np.full(self.dim, val, dtype=np.float32)
            # Add positional variation
            for i in range(self.dim):
                vec[i] += (i + 1) * 0.1
            norm = np.linalg.norm(vec)
            if norm > 0 and normalize_embeddings:
                vec = vec / norm
            matrix.append(vec)

        return np.array(matrix, dtype=np.float32)


@pytest.fixture
def mock_embedder(monkeypatch) -> SentenceEmbedder:
    """Fixture providing a fast, deterministic SentenceEmbedder with monkeypatched model."""
    embedder = SentenceEmbedder(model_name="mock-model")
    embedder._model = MockSentenceTransformer(dim=16)
    return embedder
