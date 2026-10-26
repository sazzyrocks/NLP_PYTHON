"""Unit tests for sentence embedder and vector similarity."""

import numpy as np

from src.embedder import (
    chunk_text,
    cosine_similarity_score,
)


def test_cosine_similarity_score_bounds():
    """Verify similarity values are strictly within [0.0, 100.0]."""
    v1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v2 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    assert cosine_similarity_score(v1, v2) == 100.0

    # Orthogonal
    v3 = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    assert cosine_similarity_score(v1, v3) == 0.0

    # Opposite (should be clamped to 0.0, not negative)
    v4 = np.array([-1.0, 0.0, 0.0], dtype=np.float32)
    assert cosine_similarity_score(v1, v4) == 0.0


def test_cosine_similarity_score_zero_vector():
    """Verify zero norm vectors return 0.0 without divide by zero."""
    v1 = np.zeros(5, dtype=np.float32)
    v2 = np.ones(5, dtype=np.float32)
    assert cosine_similarity_score(v1, v2) == 0.0
    assert cosine_similarity_score(v1, v1) == 0.0


def test_chunk_text_short():
    """Short text below chunk_size should return single chunk."""
    text = "This is a short sentence for testing chunking."
    chunks = chunk_text(text, chunk_size=20)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_long():
    """Long text should be divided into overlapping chunks."""
    words = [f"word{i}" for i in range(100)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=30, overlap=10)
    assert len(chunks) >= 4
    # Check overlap
    first_chunk_words = chunks[0].split()
    second_chunk_words = chunks[1].split()
    assert first_chunk_words[-10:] == second_chunk_words[:10]


def test_chunk_text_empty():
    """Empty or whitespace text returns empty list."""
    assert chunk_text("") == []
    assert chunk_text("    ") == []


def test_mock_embedder_encode_and_similarity(mock_embedder):
    """Test encode and similarity methods using deterministic mock embedder."""
    embs = mock_embedder.encode(["Python developer", "Java developer"])
    assert embs.shape == (2, 16)

    # Identical texts should have 100% similarity
    sim_identical = mock_embedder.similarity("Python developer", "Python developer")
    assert sim_identical == 100.0

    # Different texts should have valid score
    sim_diff = mock_embedder.similarity("Python developer", "Accountant")
    assert 0.0 <= sim_diff <= 100.0


def test_mock_embedder_empty_input(mock_embedder):
    """Test empty input handling in embedder."""
    assert mock_embedder.encode([]).shape == (0, 384)
    assert mock_embedder.similarity("", "text") == 0.0
    assert mock_embedder.similarity("text", "") == 0.0
    assert mock_embedder.compute_max_chunk_similarity("", "text") == 0.0
    assert mock_embedder.compute_max_chunk_similarity("text", "") == 0.0


def test_mock_embedder_max_chunk_similarity(mock_embedder):
    """Test chunk-wise max similarity calculation."""
    long_doc = " ".join([f"token_{i}" for i in range(250)])
    ref_doc = "token_1 token_2 reference"
    score = mock_embedder.compute_max_chunk_similarity(
        long_text=long_doc,
        reference_text=ref_doc,
        chunk_size=50,
        overlap=10,
    )
    assert 0.0 <= score <= 100.0
