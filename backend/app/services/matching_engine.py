"""
Matching Engine – calculates candidate-job compatibility score.

Score is computed across 5 factors using configurable weights:
  skill_score       × 0.35
  semantic_score    × 0.30
  experience_score  × 0.15
  education_score   × 0.10
  preference_score  × 0.10
  ─────────────────────────
  overall_score     normalized 0–100

No random numbers. Every score is computed from actual candidate/job data.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from app.ai.embeddings import (
    build_candidate_text,
    build_job_text,
    cosine_similarity,
    get_embedding,
    json_to_embedding,
)
from app.ai.skill_taxonomy import get_related_skills
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class MatchResult:
    overall_score: float        # 0–100
    skill_score: float          # 0–100
    semantic_score: float       # 0–100
    experience_score: float     # 0–100
    education_score: float      # 0–100
    preference_score: float     # 0–100
    explanation: Dict[str, Any]


def _normalize(value: float, min_v: float = 0.0, max_v: float = 1.0) -> float:
    """Clamp a value to 0–100 range."""
    return round(max(0.0, min(100.0, (value - min_v) / (max_v - min_v) * 100)), 2)


# ── 1. Skill Match ────────────────────────────────────────────────────
def compute_skill_score(
    candidate_skills: List[str],
    required_skills: List[str],
    preferred_skills: Optional[List[str]] = None,
) -> float:
    """
    Skill match score using Jaccard-like coefficient with partial credit
    for related skills.

    matching_skill    → full credit (1.0)
    related_skill     → partial credit (0.5)
    missing_skill     → no credit (0.0)
    """
    if not required_skills:
        return 80.0  # No skills listed → neutral high score

    candidate_set: Set[str] = {s.lower() for s in candidate_skills}
    total_weight = len(required_skills)
    earned = 0.0

    for skill in required_skills:
        skill_lower = skill.lower()
        if skill_lower in candidate_set or skill in candidate_skills:
            earned += 1.0
        else:
            # Check for related skills (partial credit)
            related = get_related_skills(skill)
            for rel in related:
                if rel.lower() in candidate_set:
                    earned += 0.5
                    break

    # Bonus for preferred skills
    if preferred_skills:
        bonus = 0.0
        for skill in preferred_skills:
            if skill.lower() in candidate_set:
                bonus += 0.5
        total_weight += len(preferred_skills) * 0.5
        earned += min(bonus, len(preferred_skills) * 0.5)

    ratio = earned / total_weight if total_weight > 0 else 0.0
    return round(ratio * 100, 2)


# ── 2. Semantic Similarity ────────────────────────────────────────────
def compute_semantic_score(
    candidate_embedding: Optional[List[float]],
    job_embedding: Optional[List[float]],
    candidate_data: Optional[Dict] = None,
    job_data: Optional[Dict] = None,
) -> float:
    """
    Compute semantic similarity via cosine similarity on embeddings.
    Falls back to generating embeddings on-the-fly if cached embeddings unavailable.
    """
    if not candidate_embedding and candidate_data:
        candidate_text = build_candidate_text(candidate_data)
        candidate_embedding = get_embedding(candidate_text)

    if not job_embedding and job_data:
        job_text = build_job_text(job_data)
        job_embedding = get_embedding(job_text)

    if not candidate_embedding or not job_embedding:
        return 50.0  # Neutral if embeddings unavailable

    sim = cosine_similarity(candidate_embedding, job_embedding)
    # cosine similarity is in [-1, 1]; normalize to 0–100
    return round(((sim + 1) / 2) * 100, 2)


# ── 3. Experience Match ───────────────────────────────────────────────
def compute_experience_score(
    candidate_years: float,
    job_exp_min: Optional[float],
    job_exp_max: Optional[float],
) -> float:
    """
    Score based on how well candidate's experience matches job requirements.
    """
    if job_exp_min is None and job_exp_max is None:
        return 80.0  # No requirement stated → neutral

    exp_min = job_exp_min or 0.0
    exp_max = job_exp_max or (exp_min + 5.0)

    if candidate_years >= exp_min and candidate_years <= exp_max:
        return 100.0  # Perfect fit
    elif candidate_years < exp_min:
        deficit = exp_min - candidate_years
        penalty = min(deficit * 15, 70)  # Max 70 point penalty
        return round(100.0 - penalty, 2)
    else:
        # Over-experienced – slight penalty
        excess = candidate_years - exp_max
        penalty = min(excess * 5, 20)
        return round(100.0 - penalty, 2)


# ── 4. Education Match ────────────────────────────────────────────────
DEGREE_TO_LEVEL = {
    "phd": 7, "doctorate": 7,
    "mba": 6, "mtech": 6, "me": 6, "msc": 6, "mca": 6, "ms": 6, "masters": 6,
    "btech": 5, "be": 5, "bsc": 5, "bca": 5, "ba": 5, "bcom": 5, "bba": 5, "bachelors": 5,
    "diploma": 3,
    "12th": 2, "hsc": 2, "intermediate": 2,
    "10th": 1, "ssc": 1,
}

def compute_education_score(
    candidate_degree: Optional[str],
    candidate_degree_level: int,
    job_education_required: Optional[str],
) -> float:
    """Score based on degree level comparison."""
    if not job_education_required:
        return 80.0  # No requirement

    req_clean = re.sub(r"[^\w\s]", "", job_education_required.lower())
    matched_levels = [level for keyword, level in DEGREE_TO_LEVEL.items() if keyword in req_clean]
    req_level = min(matched_levels) if matched_levels else 5

    if candidate_degree_level >= req_level:
        return 100.0
    elif candidate_degree_level == req_level - 1:
        return 70.0
    elif candidate_degree_level == req_level - 2:
        return 40.0
    else:
        return 20.0


# ── 5. Preference Match ───────────────────────────────────────────────
def compute_preference_score(
    candidate_prefs: Dict[str, Any],
    job: Dict[str, Any],
) -> float:
    """
    Match candidate preferences against job attributes.
    """
    score = 0.0
    max_score = 0.0

    # Location preference
    preferred_locations = candidate_prefs.get("preferred_locations", [])
    job_location = (job.get("location") or "").lower()
    if preferred_locations:
        max_score += 30
        for loc in preferred_locations:
            if loc.lower() in job_location or job_location in loc.lower():
                score += 30
                break
    else:
        score += 25
        max_score += 25

    # Remote/work mode preference
    remote_pref = (candidate_prefs.get("remote_preference") or "any").lower()
    job_mode = (job.get("work_mode") or "").lower()
    max_score += 30
    if remote_pref == "any":
        score += 25
    elif remote_pref == job_mode:
        score += 30
    elif job_mode == "hybrid" and remote_pref in ("remote", "onsite"):
        score += 15

    # Employment type
    emp_pref = (candidate_prefs.get("employment_type") or "any").lower()
    job_type = (job.get("job_type") or "").lower()
    max_score += 20
    if emp_pref == "any" or emp_pref == job_type:
        score += 20
    elif "full" in emp_pref and "full" in job_type:
        score += 20

    # Preferred roles
    preferred_roles = candidate_prefs.get("preferred_roles", [])
    job_title = (job.get("title") or "").lower()
    if preferred_roles:
        max_score += 20
        for role in preferred_roles:
            if role.lower() in job_title or job_title in role.lower():
                score += 20
                break

    if max_score == 0:
        return 70.0

    return round((score / max_score) * 100, 2)


# ── Main Match Function ───────────────────────────────────────────────
def compute_match(
    candidate: Dict[str, Any],
    job: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None,
) -> MatchResult:
    """
    Compute full compatibility match between a candidate and a job.

    candidate dict keys:
      skills, total_experience_years, highest_degree, highest_degree_level,
      embedding (optional), preferences, summary, education, job_titles

    job dict keys:
      required_skills, preferred_skills, experience_min, experience_max,
      education_required, work_mode, job_type, location, title, description,
      embedding (optional)
    """
    w = weights or settings.match_weights

    # Extract candidate data
    candidate_skills = candidate.get("skills", [])
    candidate_years = candidate.get("total_experience_years", 0.0)
    candidate_degree = candidate.get("highest_degree")
    candidate_degree_level = candidate.get("highest_degree_level", 0)
    if not candidate_degree_level and candidate.get("education"):
        for edu in candidate.get("education", []):
            deg = (edu.get("degree") or "").lower()
            for kw, lvl in DEGREE_TO_LEVEL.items():
                if kw in deg and lvl > candidate_degree_level:
                    candidate_degree_level = lvl
                    candidate_degree = edu.get("degree")
    candidate_embedding = candidate.get("embedding")
    candidate_prefs = candidate.get("preferences", {})

    # Extract job data
    raw_skills = job.get("required_skills") or job.get("skills", [])
    job_required_skills = [
        s["skill_name"] if isinstance(s, dict) else s
        for s in raw_skills
        if not isinstance(s, dict) or s.get("is_required", True)
    ]
    raw_pref = job.get("preferred_skills") or []
    if not raw_pref and "skills" in job:
        raw_pref = [s["skill_name"] for s in job["skills"] if isinstance(s, dict) and not s.get("is_required", True)]
    job_preferred_skills = [s["skill_name"] if isinstance(s, dict) else s for s in raw_pref]
    job_exp_min = job.get("experience_min")
    job_exp_max = job.get("experience_max")
    job_education = job.get("education_required")
    job_embedding = job.get("embedding")

    # 1. Skill score
    skill_score = compute_skill_score(candidate_skills, job_required_skills, job_preferred_skills)

    # 2. Semantic score
    semantic_score = compute_semantic_score(
        candidate_embedding,
        json_to_embedding(job_embedding) if isinstance(job_embedding, str) else job_embedding,
        candidate_data=candidate,
        job_data=job,
    )

    # 3. Experience score
    experience_score = compute_experience_score(candidate_years, job_exp_min, job_exp_max)

    # 4. Education score
    education_score = compute_education_score(candidate_degree, candidate_degree_level, job_education)

    # 5. Preference score
    preference_score = compute_preference_score(candidate_prefs, job)

    # Weighted overall score (0–100)
    overall = (
        skill_score * w["skills"]
        + semantic_score * w["semantic"]
        + experience_score * w["experience"]
        + education_score * w["education"]
        + preference_score * w["preferences"]
    )
    overall = round(min(100.0, max(0.0, overall)), 2)

    # Build matching / missing skill lists for explanation
    candidate_set = {s.lower() for s in candidate_skills}
    matched = [s for s in job_required_skills if s.lower() in candidate_set]
    missing = [s for s in job_required_skills if s.lower() not in candidate_set]

    explanation = {
        "weights_used": w,
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_score": skill_score,
        "semantic_score": semantic_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "preference_score": preference_score,
        "candidate_experience_years": candidate_years,
        "required_experience_min": job_exp_min,
        "required_experience_max": job_exp_max,
        "candidate_degree": candidate_degree,
        "required_education": job_education,
    }

    return MatchResult(
        overall_score=overall,
        skill_score=skill_score,
        semantic_score=semantic_score,
        experience_score=experience_score,
        education_score=education_score,
        preference_score=preference_score,
        explanation=explanation,
    )
