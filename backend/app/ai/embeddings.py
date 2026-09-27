"""
Embedding service using sentence-transformers.
Supports caching embeddings to avoid redundant computation.
Falls back to TF-IDF if sentence-transformers unavailable.
"""
from __future__ import annotations

import json
import hashlib
from typing import List, Optional

import numpy as np

from app.utils.logger import get_logger

logger = get_logger(__name__)

_model = None
_use_tfidf_fallback = False


def _get_model():
    global _model, _use_tfidf_fallback
    if _model is None and not _use_tfidf_fallback:
        try:
            from sentence_transformers import SentenceTransformer
            from app.config import get_settings
            settings = get_settings()
            model_name = settings.EMBEDDING_MODEL or "sentence-transformers/all-MiniLM-L6-v2"
            _model = SentenceTransformer(model_name)
            logger.info(f"Sentence-transformer model loaded: {model_name}")
        except Exception as e:
            logger.warning(f"sentence-transformers unavailable ({e}), using TF-IDF fallback")
            _use_tfidf_fallback = True
    return _model


def _text_hash(text: str) -> str:
    """Compute deterministic hash for cache keying."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text.
    Uses sentence-transformers if available, else TF-IDF.
    """
    if not text or not text.strip():
        return [0.0] * 384  # Default all-MiniLM-L6-v2 dims

    model = _get_model()
    if model:
        try:
            embedding = model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")

    # TF-IDF fallback
    return _tfidf_embedding(text)


def _tfidf_embedding(text: str, dim: int = 384) -> List[float]:
    """
    Simple TF-IDF-inspired sparse embedding as fallback.
    Not as powerful as sentence-transformers but deterministic.
    """
    import re

    words = re.findall(r"\w+", text.lower())
    if not words:
        return [0.0] * dim

    # Count frequencies
    freq: dict = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1

    # Create sparse hash-based vector
    vec = np.zeros(dim)
    total = len(words)
    for word, count in freq.items():
        idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % dim
        vec[idx] += count / total

    # Normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    if not vec_a or not vec_b:
        return 0.0
    a = np.array(vec_a)
    b = np.array(vec_b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def embedding_to_json(embedding: List[float]) -> str:
    """Serialize embedding to JSON string for DB storage."""
    return json.dumps(embedding)


def json_to_embedding(json_str: str) -> Optional[List[float]]:
    """Deserialize embedding from DB JSON string."""
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except Exception:
        return None


def build_candidate_text(profile_data: dict) -> str:
    """
    Create a rich text representation of candidate for embedding.
    Combines skills, education, experience, and summary.
    """
    parts = []
    if profile_data.get("summary"):
        parts.append(profile_data["summary"])
    if profile_data.get("skills"):
        parts.append("Skills: " + ", ".join(profile_data["skills"]))
    if profile_data.get("highest_degree"):
        parts.append(f"Education: {profile_data['highest_degree']}")
    if profile_data.get("job_titles"):
        parts.append("Experience: " + ", ".join(profile_data["job_titles"]))
    if profile_data.get("total_experience_years"):
        parts.append(f"{profile_data['total_experience_years']} years of experience")
    return " ".join(parts)


def build_job_text(job: dict) -> str:
    """
    Create a rich text representation of a job for embedding.
    """
    parts = []
    if job.get("title"):
        parts.append(job["title"])
    if job.get("company"):
        parts.append(f"at {job['company']}")
    if job.get("description"):
        # Use first 1000 chars of description
        parts.append(job["description"][:1000])
    if job.get("skills"):
        skills = [s["skill_name"] if isinstance(s, dict) else s for s in job.get("skills", [])]
        parts.append("Required skills: " + ", ".join(skills))
    return " ".join(parts)
