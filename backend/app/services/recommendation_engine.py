"""
Recommendation Engine – generates ranked job recommendations for a candidate.

Pipeline:
  Candidate Profile → Retrieve Jobs → Score (matching_engine) →
  Sort by score → Apply Preferences → Remove dups → Return with Explanation + Skill Gap

Explanation is structured data (not a random string).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.ai.embeddings import (
    build_candidate_text,
    embedding_to_json,
    get_embedding,
    json_to_embedding,
)
from app.models import (
    CandidateEducation,
    CandidateExperience,
    CandidateSkill,
    Job,
    JobSkill,
    Profile,
    Recommendation,
    SkillGap,
    UserPreference,
)
from app.services.matching_engine import compute_match
from app.services.skill_gap import analyze_skill_gap
from app.utils.logger import get_logger

logger = get_logger(__name__)


def build_candidate_dict(
    user_id: int,
    db: Session,
    include_embedding: bool = True,
) -> Dict[str, Any]:
    """
    Build a candidate representation dict from DB data.
    """
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    prefs = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    skills_rows = db.query(CandidateSkill).filter(CandidateSkill.user_id == user_id).all()
    edu_rows = db.query(CandidateEducation).filter(CandidateEducation.user_id == user_id).all()
    exp_rows = db.query(CandidateExperience).filter(CandidateExperience.user_id == user_id).all()

    skills = [s.skill_name for s in skills_rows]
    education = [
        {
            "degree": e.degree,
            "institution": e.institution,
            "graduation_year": e.graduation_year,
        }
        for e in edu_rows
    ]
    experience = [
        {
            "job_title": e.job_title,
            "company": e.company,
            "duration_months": e.duration_months,
        }
        for e in exp_rows
    ]

    # Compute highest degree level
    from app.services.matching_engine import DEGREE_TO_LEVEL
    highest_degree = None
    highest_level = 0
    for edu in edu_rows:
        if edu.degree:
            lvl = DEGREE_TO_LEVEL.get(edu.degree.lower(), 0)
            if lvl > highest_level:
                highest_level = lvl
                highest_degree = edu.degree

    prefs_dict = {}
    if prefs:
        prefs_dict = {
            "preferred_roles": json.loads(prefs.preferred_roles or "[]"),
            "preferred_locations": json.loads(prefs.preferred_locations or "[]"),
            "remote_preference": prefs.remote_preference or "any",
            "employment_type": prefs.employment_type or "any",
        }

    candidate = {
        "user_id": user_id,
        "skills": skills,
        "education": education,
        "experience": experience,
        "total_experience_years": profile.experience_years if profile else 0.0,
        "highest_degree": highest_degree,
        "highest_degree_level": highest_level,
        "job_titles": [e.job_title for e in exp_rows if e.job_title],
        "preferences": prefs_dict,
        "summary": profile.bio if profile else None,
        "embedding": None,
    }

    if include_embedding:
        # Build or retrieve cached embedding
        embedding_text = build_candidate_text(candidate)
        embedding = get_embedding(embedding_text)
        candidate["embedding"] = embedding

    return candidate


def build_job_dict(job: Job) -> Dict[str, Any]:
    """Convert a Job ORM object to a dict suitable for matching."""
    required_skills = [s.skill_name for s in job.skills if s.is_required]
    preferred_skills = [s.skill_name for s in job.skills if not s.is_required]
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience_min": job.experience_min,
        "experience_max": job.experience_max,
        "education_required": job.education_required,
        "job_type": job.job_type,
        "work_mode": job.work_mode,
        "embedding": job.embedding,  # JSON string
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
    }


def generate_explanation_text(match_result, candidate: dict, job: dict) -> Dict[str, Any]:
    """
    Generate structured explanation for why a job is recommended.
    Returns a dict with human-readable reasoning.
    """
    exp = match_result.explanation
    matched = exp.get("matched_skills", [])
    missing = exp.get("missing_skills", [])

    reasons = []
    if matched:
        reasons.append(f"You have {len(matched)} of the required skills: {', '.join(matched[:5])}")
    if exp.get("candidate_degree"):
        reasons.append(f"Your {exp['candidate_degree']} qualification is relevant for this role")
    years = exp.get("candidate_experience_years", 0)
    if years > 0:
        req_min = exp.get("required_experience_min")
        if req_min and years >= req_min:
            reasons.append(f"Your {years} years of experience meets the requirement")
        elif req_min and years < req_min:
            reasons.append(f"You have {years} years exp; role requires {req_min}+ years")

    return {
        "overall_score": match_result.overall_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "reasons": reasons,
        "score_breakdown": {
            "skill_match": f"{match_result.skill_score:.1f}%",
            "semantic_similarity": f"{match_result.semantic_score:.1f}%",
            "experience_match": f"{match_result.experience_score:.1f}%",
            "education_match": f"{match_result.education_score:.1f}%",
            "preference_match": f"{match_result.preference_score:.1f}%",
        },
        "weights_used": exp.get("weights_used", {}),
    }


def compute_recommendations(
    user_id: int,
    db: Session,
    limit: int = 50,
    min_score: float = 0.0,
) -> List[Recommendation]:
    """
    Compute and store recommendations for a user.
    Returns list of stored Recommendation records.
    """
    logger.info(f"Computing recommendations for user {user_id}")

    candidate = build_candidate_dict(user_id, db)
    if not candidate["skills"] and candidate["total_experience_years"] == 0:
        logger.warning(f"User {user_id} has no profile data for recommendations")

    # Retrieve active, non-duplicate jobs
    jobs = db.query(Job).filter(Job.is_active == True, Job.processed == True).all()
    if not jobs:
        logger.warning("No processed jobs found for recommendations")
        return []

    scored_jobs = []
    for job in jobs:
        job_dict = build_job_dict(job)
        try:
            match = compute_match(candidate, job_dict)
            if match.overall_score >= min_score:
                scored_jobs.append((job, match))
        except Exception as e:
            logger.error(f"Match error for job {job.id}: {e}")

    # Sort by overall score descending
    scored_jobs.sort(key=lambda x: x[1].overall_score, reverse=True)

    recommendations = []
    for job, match in scored_jobs[:limit]:
        # Upsert recommendation record
        rec = db.query(Recommendation).filter(
            Recommendation.user_id == user_id,
            Recommendation.job_id == job.id,
        ).first()

        explanation = generate_explanation_text(match, candidate, build_job_dict(job))

        if rec:
            rec.overall_score = match.overall_score
            rec.skill_score = match.skill_score
            rec.semantic_score = match.semantic_score
            rec.experience_score = match.experience_score
            rec.education_score = match.education_score
            rec.preference_score = match.preference_score
            rec.explanation = json.dumps(explanation)
            rec.computed_at = datetime.now(timezone.utc)
        else:
            rec = Recommendation(
                user_id=user_id,
                job_id=job.id,
                overall_score=match.overall_score,
                skill_score=match.skill_score,
                semantic_score=match.semantic_score,
                experience_score=match.experience_score,
                education_score=match.education_score,
                preference_score=match.preference_score,
                explanation=json.dumps(explanation),
            )
            db.add(rec)
        db.flush()

        # Store skill gaps
        job_skills = [s.skill_name for s in job.skills if s.is_required]
        gap_result = analyze_skill_gap(candidate["skills"], job_skills)

        # Delete old gaps for this user-job pair
        db.query(SkillGap).filter(
            SkillGap.user_id == user_id,
            SkillGap.job_id == job.id,
        ).delete()

        for skill in gap_result.matching:
            db.add(SkillGap(user_id=user_id, job_id=job.id, skill_name=skill, gap_type="matching"))
        for skill in gap_result.partial:
            db.add(SkillGap(user_id=user_id, job_id=job.id, skill_name=skill, gap_type="partial"))
        for skill in gap_result.missing:
            db.add(SkillGap(user_id=user_id, job_id=job.id, skill_name=skill, gap_type="missing"))

        recommendations.append(rec)

    db.commit()
    logger.info(f"Stored {len(recommendations)} recommendations for user {user_id}")
    return recommendations
