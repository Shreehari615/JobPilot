"""
Recommendations router – ranked job recommendations, explanations, skill gaps.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    CandidateSkill,
    Job,
    JobSkill,
    Profile,
    Recommendation,
    SkillGap,
    User,
)
from app.schemas import (
    JobDetailOut,
    JobOut,
    RecommendationDetailOut,
    RecommendationOut,
    SkillGapOut,
)
from app.services.recommendation_engine import compute_recommendations
from app.utils.dependencies import get_current_user
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def _format_job_out(job: Job, detail: bool = False) -> Any:
    if not job:
        return None
    skills = [{"skill_name": s.skill_name, "is_required": s.is_required} for s in job.skills]
    base_data = {
        "id": job.id,
        "external_id": job.external_id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "salary_currency": job.salary_currency or "INR",
        "job_type": job.job_type,
        "work_mode": job.work_mode,
        "experience_min": job.experience_min,
        "experience_max": job.experience_max,
        "education_required": job.education_required,
        "original_url": job.original_url,
        "posted_date": job.posted_date,
        "collected_at": job.collected_at,
        "is_seed_data": job.is_seed_data,
        "source_name": job.source.name if job.source else None,
        "skills": skills,
    }
    if detail:
        base_data["responsibilities"] = job.responsibilities
        return JobDetailOut(**base_data)
    return JobOut(**base_data)


@router.get("", response_model=List[RecommendationOut])
def get_recommendations(
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=100.0),
    recompute: bool = Query(False, description="Force recomputation if True"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve ranked job recommendations for the authenticated candidate.
    Requires an uploaded & parsed resume (skills present). Returns [] if no
    resume has been processed yet so that meaningless neutral scores are never
    shown to the user.
    """
    # ── Resume gate ──────────────────────────────────────────────────────
    has_skills = (
        db.query(CandidateSkill)
        .filter(CandidateSkill.user_id == current_user.id)
        .first()
    )
    if not has_skills:
        logger.info(
            f"User {current_user.id} has no parsed resume skills – "
            "returning empty recommendations."
        )
        return []
    # ─────────────────────────────────────────────────────────────────────

    recs = (
        db.query(Recommendation)
        .filter(
            Recommendation.user_id == current_user.id,
            Recommendation.overall_score >= min_score,
        )
        .order_by(Recommendation.overall_score.desc())
        .limit(limit)
        .all()
    )

    if not recs or recompute:
        logger.info(f"Computing recommendations for user {current_user.id} (fresh or forced)")
        try:
            recs = compute_recommendations(user_id=current_user.id, db=db, limit=limit, min_score=min_score)
        except Exception as e:
            logger.error(f"Error computing recommendations: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate recommendations: {str(e)}",
            )

    results = []
    for r in recs:
        exp_dict = json.loads(r.explanation) if isinstance(r.explanation, str) else (r.explanation or {})
        results.append(
            RecommendationOut(
                id=r.id,
                job_id=r.job_id,
                overall_score=r.overall_score,
                skill_score=r.skill_score,
                semantic_score=r.semantic_score,
                experience_score=r.experience_score,
                education_score=r.education_score,
                preference_score=r.preference_score,
                explanation=exp_dict,
                computed_at=r.computed_at,
                job=_format_job_out(r.job),
            )
        )
    return results


@router.post("/recompute", response_model=List[RecommendationOut])
def trigger_recompute(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Force recomputation of recommendations based on updated resume or profile.
    Requires a parsed resume.
    """
    # ── Resume gate ──────────────────────────────────────────────────────
    has_skills = (
        db.query(CandidateSkill)
        .filter(CandidateSkill.user_id == current_user.id)
        .first()
    )
    if not has_skills:
        logger.info(
            f"User {current_user.id} triggered recompute but has no parsed "
            "resume skills – skipping."
        )
        return []
    # ─────────────────────────────────────────────────────────────────────

    try:
        recs = compute_recommendations(user_id=current_user.id, db=db, limit=limit)
    except Exception as e:
        logger.error(f"Recomputation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recomputation failed: {str(e)}",
        )

    results = []
    for r in recs:
        exp_dict = json.loads(r.explanation) if isinstance(r.explanation, str) else (r.explanation or {})
        results.append(
            RecommendationOut(
                id=r.id,
                job_id=r.job_id,
                overall_score=r.overall_score,
                skill_score=r.skill_score,
                semantic_score=r.semantic_score,
                experience_score=r.experience_score,
                education_score=r.education_score,
                preference_score=r.preference_score,
                explanation=exp_dict,
                computed_at=r.computed_at,
                job=_format_job_out(r.job),
            )
        )
    return results


@router.get("/job/{job_id}", response_model=RecommendationDetailOut)
def get_recommendation_for_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed match score, explanations, and skill gaps for a specific job.
    Requires a parsed resume; returns zeroed-out scores otherwise.
    """
    job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    # ── Resume gate ──────────────────────────────────────────────────────
    has_skills = (
        db.query(CandidateSkill)
        .filter(CandidateSkill.user_id == current_user.id)
        .first()
    )
    if not has_skills:
        return RecommendationDetailOut(
            id=0,
            job_id=job.id,
            overall_score=0.0,
            skill_score=0.0,
            semantic_score=0.0,
            experience_score=0.0,
            education_score=0.0,
            preference_score=0.0,
            explanation={"resume_required": True},
            computed_at=None,
            skill_gaps=[],
            job=_format_job_out(job, detail=True),
        )
    # ─────────────────────────────────────────────────────────────────────

    rec = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == current_user.id, Recommendation.job_id == job_id)
        .first()
    )

    # If recommendation doesn't exist yet, compute on the fly
    if not rec:
        compute_recommendations(user_id=current_user.id, db=db, limit=50)
        rec = (
            db.query(Recommendation)
            .filter(Recommendation.user_id == current_user.id, Recommendation.job_id == job_id)
            .first()
        )

    # Get skill gaps
    gaps = (
        db.query(SkillGap)
        .filter(SkillGap.user_id == current_user.id, SkillGap.job_id == job_id)
        .all()
    )
    gap_outs = [SkillGapOut(skill_name=g.skill_name, gap_type=g.gap_type) for g in gaps]

    exp_dict = {}
    if rec and rec.explanation:
        exp_dict = json.loads(rec.explanation) if isinstance(rec.explanation, str) else rec.explanation

    return RecommendationDetailOut(
        id=rec.id if rec else 0,
        job_id=job.id,
        overall_score=rec.overall_score if rec else 0.0,
        skill_score=rec.skill_score if rec else 0.0,
        semantic_score=rec.semantic_score if rec else 0.0,
        experience_score=rec.experience_score if rec else 0.0,
        education_score=rec.education_score if rec else 0.0,
        preference_score=rec.preference_score if rec else 0.0,
        explanation=exp_dict,
        computed_at=rec.computed_at if rec else None,
        skill_gaps=gap_outs,
        job=_format_job_out(job, detail=True),
    )
