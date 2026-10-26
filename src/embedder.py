"""Sentence embeddings and semantic similarity module using sentence-transformers."""

import os
from typing import List, Optional, Union
import numpy as np
from sentence_transformers import SentenceTransformer

# Suppress verbose warnings
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


def cosine_similarity_score(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors and scale to 0-100.

    Args:
        vec_a: 1D array representing first embedding vector.
        vec_b: 1D array representing second embedding vector.

    Returns:
        Similarity score clipped between 0.0 and 100.0.
    """
    vec_a = np.asarray(vec_a, dtype=np.float32).ravel()
    vec_b = np.asarray(vec_b, dtype=np.float32).ravel()

    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    raw_cos = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
    # Clip between 0.0 and 1.0 (negative similarity clamped to 0)
    clipped = max(0.0, min(1.0, raw_cos))
    return round(clipped * 100.0, 2)


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 30) -> List[str]:
    """Split long text into overlapping chunks of approximately chunk_size words.

    Args:
        text: Text to divide.
        chunk_size: Target number of words per chunk.
        overlap: Number of overlapping words between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if not text or not text.strip():
        return []

    words = text.split()
    if len(words) <= chunk_size:
        return [text.strip()]

    chunks = []
    step = max(1, chunk_size - overlap)
    for start_idx in range(0, len(words), step):
        chunk_words = words[start_idx : start_idx + chunk_size]
        chunk = " ".join(chunk_words).strip()
        if chunk:
            chunks.append(chunk)
        if start_idx + chunk_size >= len(words):
            break

    return chunks


class SentenceEmbedder:
    """Manages sentence embedding model loading, encoding, and chunk-wise similarity."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize embedder with specified sentence-transformers model.

        Args:
            model_name: HuggingFace model name or path.
        """
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy loader for SentenceTransformer model."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate normalized embeddings for one or more text inputs.

        Args:
            texts: Single string or list of text strings.

        Returns:
            2D numpy array of embeddings (shape: [N, D]).
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.asarray(embeddings, dtype=np.float32)

    def similarity(
        self,
        text_a: str,
        text_b: str,
    ) -> float:
        """Compute semantic similarity between two texts (0 to 100).

        Args:
            text_a: First text string.
            text_b: Second text string.

        Returns:
            Similarity score scaled to 0-100.
        """
        if not text_a.strip() or not text_b.strip():
            return 0.0

        embs = self.encode([text_a, text_b])
        return cosine_similarity_score(embs[0], embs[1])

    def compute_max_chunk_similarity(
        self,
        long_text: str,
        reference_text: str,
        chunk_size: int = 200,
        overlap: int = 30,
    ) -> float:
        """Compute the maximum similarity score among chunks of long_text vs reference_text.

        Args:
            long_text: Typically the candidate resume or section text.
            reference_text: Typically the Job Description text.
            chunk_size: Word count per chunk.
            overlap: Word overlap count.

        Returns:
            Highest chunk similarity score clipped to 0-100.
        """
        if not long_text.strip() or not reference_text.strip():
            return 0.0

        chunks = chunk_text(long_text, chunk_size=chunk_size, overlap=overlap)
        if not chunks:
            return 0.0

        # Encode reference text once
        ref_emb = self.encode([reference_text])[0]

        # Encode all chunks in a single batch
        chunk_embs = self.encode(chunks)

        max_score = 0.0
        for emb in chunk_embs:
            score = cosine_similarity_score(emb, ref_emb)
            if score > max_score:
                max_score = score

        return max_score


_GLOBAL_EMBEDDER: Optional[SentenceEmbedder] = None


def get_embedder() -> SentenceEmbedder:
    """Singleton getter for the global SentenceEmbedder."""
    global _GLOBAL_EMBEDDER
    if _GLOBAL_EMBEDDER is None:
        _GLOBAL_EMBEDDER = SentenceEmbedder()
    return _GLOBAL_EMBEDDER
