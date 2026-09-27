"""
Admin router – job collection triggers, source management, statistics, deduplication inspect.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.job_sources.seed_source import SeedDataSource
from app.models import (
    Job,
    JobDuplicate,
    JobSource,
    Recommendation,
    User,
)
from app.schemas import AdminStatsOut, JobSourceOut
from app.services.job_service import collect_and_store_jobs
from app.utils.dependencies import get_current_admin_user
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStatsOut)
def get_admin_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
):
    """
    Overview statistics for platform administration.
    """
    total_jobs = db.query(Job).count()
    active_jobs = db.query(Job).filter(Job.is_active == True).count()
    seed_jobs = db.query(Job).filter(Job.is_seed_data == True).count()
    total_users = db.query(User).count()
    total_recommendations = db.query(Recommendation).count()
    duplicate_groups = db.query(func.count(distinct(JobDuplicate.primary_job_id))).scalar() or 0
    job_sources = db.query(JobSource).count()

    return AdminStatsOut(
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        seed_jobs=seed_jobs,
        total_users=total_users,
        total_recommendations=total_recommendations,
        duplicate_groups=duplicate_groups,
        job_sources=job_sources,
    )


@router.get("/sources", response_model=List[JobSourceOut])
def list_job_sources(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
):
    """
    List all configured job sources and their health metrics.
    """
    sources = db.query(JobSource).order_by(JobSource.name).all()
    return sources


@router.post("/collect")
def trigger_job_collection(
    max_per_source: int = Query(50, ge=5, le=200),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
):
    """
    Manually trigger job collection from all enabled sources.
    Executes cleaning, normalization, dedup, embedding, and storage.
    """
    try:
        stats = collect_and_store_jobs(db, max_per_source=max_per_source)
        return {
            "status": "success",
            "message": "Job collection finished successfully",
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Collection execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Collection failed: {str(e)}",
        )


@router.get("/duplicates")
def list_duplicate_pairs(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user),
):
    """
    View detected duplicate jobs with similarity score and detection level.
    """
    dups = (
        db.query(JobDuplicate)
        .order_by(JobDuplicate.detected_at.desc())
        .limit(limit)
        .all()
    )

    results = []
    for d in dups:
        results.append({
            "id": d.id,
            "primary_job_id": d.primary_job_id,
            "duplicate_job_id": d.duplicate_job_id,
            "similarity_score": d.similarity_score,
            "detection_level": d.detection_level,
            "detected_at": d.detected_at,
            "primary_job": {
                "title": d.primary_job.title if d.primary_job else None,
                "company": d.primary_job.company if d.primary_job else None,
            },
            "duplicate_job": {
                "title": d.duplicate_job.title if d.duplicate_job else None,
                "company": d.duplicate_job.company if d.duplicate_job else None,
            },
        })
    return results
