"""
Duplicate Detector – three-level deduplication.

Level 1 – Exact:     same external_id or same URL
Level 2 – Structured: same company + title + location (normalized)
Level 3 – Semantic:  description embedding cosine similarity above threshold

Does NOT delete duplicates – marks them in job_duplicates table for grouping.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from app.ai.embeddings import cosine_similarity, get_embedding, json_to_embedding
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def _normalize_str(s: Optional[str]) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def _structured_key(company: str, title: str, location: str) -> str:
    """Create a normalized composite key for Level 2 detection."""
    return f"{_normalize_str(company)}|{_normalize_str(title)}|{_normalize_str(location)}"


def check_exact_duplicate(
    new_external_id: Optional[str],
    new_url: str,
    existing_jobs: List[Dict],
) -> Optional[int]:
    """
    Level 1: Check if a job with the same external_id or URL already exists.
    Returns the ID of the existing job if duplicate found, else None.
    """
    new_url_norm = (new_url or "").rstrip("/").lower()
    for job in existing_jobs:
        if new_external_id and job.get("external_id") == new_external_id:
            return job["id"]
        existing_url = (job.get("original_url") or "").rstrip("/").lower()
        if new_url_norm and new_url_norm == existing_url:
            return job["id"]
    return None


def check_structured_duplicate(
    company: str,
    title: str,
    location: str,
    existing_structured_keys: Dict[str, int],
) -> Optional[int]:
    """
    Level 2: Check if job with same company+title+location already exists.
    Returns the ID of the existing job if duplicate found, else None.
    """
    key = _structured_key(company, title, location)
    return existing_structured_keys.get(key)


def check_semantic_duplicate(
    new_description: str,
    existing_embeddings: List[Tuple[int, List[float]]],
    threshold: Optional[float] = None,
) -> Optional[Tuple[int, float]]:
    """
    Level 3: Check if job description is semantically similar to existing jobs.
    Returns (existing_job_id, similarity_score) if above threshold, else None.
    """
    if not new_description or not existing_embeddings:
        return None

    threshold = threshold or settings.DEDUP_SEMANTIC_THRESHOLD
    new_embedding = get_embedding(new_description[:2000])

    best_match_id = None
    best_sim = 0.0

    for job_id, emb in existing_embeddings:
        sim = cosine_similarity(new_embedding, emb)
        if sim >= threshold and sim > best_sim:
            best_sim = sim
            best_match_id = job_id

    if best_match_id:
        return (best_match_id, best_sim)
    return None


def build_structured_key_map(jobs: List[Dict]) -> Dict[str, int]:
    """Build a lookup dict: structured_key → job_id for Level 2 detection."""
    return {
        _structured_key(
            j.get("company", ""),
            j.get("title", ""),
            j.get("location", ""),
        ): j["id"]
        for j in jobs
    }
