"""
Jobs router – search, filter, detail, saved jobs, and interaction tracking.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    ApplicationInteraction,
    Job,
    JobSkill,
    JobSource,
    SavedJob,
    User,
)
from app.schemas import (
    InteractionRequest,
    JobDetailOut,
    JobOut,
    PaginatedResponse,
    SavedJobOut,
    SaveJobRequest,
)
from app.services.job_service import collect_and_store_jobs, get_jobs_paginated
from app.utils.dependencies import get_current_user, get_optional_user
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=PaginatedResponse)
def list_jobs(
    query: Optional[str] = Query(None, description="Keywords in title, company, description"),
    location: Optional[str] = Query(None, description="Location filter"),
    job_type: Optional[str] = Query(None, description="full-time, part-time, contract, internship"),
    work_mode: Optional[str] = Query(None, description="remote, hybrid, onsite"),
    experience_min: Optional[float] = Query(None, ge=0),
    experience_max: Optional[float] = Query(None, ge=0),
    salary_min: Optional[int] = Query(None, ge=0),
    salary_max: Optional[int] = Query(None, ge=0),
    skills: Optional[str] = Query(None, description="Comma-separated skill names"),
    sort_by: str = Query("posted_date", regex="^(posted_date|salary)$"),
    real_only: Optional[bool] = Query(None, description="Filter only real market jobs"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search and filter active job postings with pagination.
    """
    skill_list = [s.strip() for s in skills.split(",") if s.strip()] if skills else None

    jobs, total = get_jobs_paginated(
        db=db,
        page=page,
        page_size=page_size,
        query=query,
        location=location,
        job_type=job_type,
        work_mode=work_mode,
        experience_min=experience_min,
        experience_max=experience_max,
        salary_min=salary_min,
        salary_max=salary_max,
        skills=skill_list,
        sort_by=sort_by,
        real_only=real_only,
    )

    items = []
    for j in jobs:
        items.append(
            JobOut(
                id=j.id,
                external_id=j.external_id,
                title=j.title,
                company=j.company,
                location=j.location,
                description=j.description,
                salary_min=j.salary_min,
                salary_max=j.salary_max,
                salary_currency=j.salary_currency or "INR",
                job_type=j.job_type,
                work_mode=j.work_mode,
                experience_min=j.experience_min,
                experience_max=j.experience_max,
                education_required=j.education_required,
                original_url=j.original_url,
                posted_date=j.posted_date,
                collected_at=j.collected_at,
                is_seed_data=j.is_seed_data,
                source_name=j.source.name if j.source else None,
                skills=[{"skill_name": s.skill_name, "is_required": s.is_required} for s in j.skills],
            )
        )

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.post("/sync")
@router.get("/sync")
def sync_live_jobs(
    max_per_source: int = Query(30, ge=5, le=100),
    db: Session = Depends(get_db),
):
    """
    Trigger real-time job collection from all active external job sources.
    Fetches real market jobs with live company URLs.
    """
    try:
        stats = collect_and_store_jobs(db, max_per_source=max_per_source)
        return {"status": "success", "message": "Live jobs synced successfully", "stats": stats}
    except Exception as e:
        logger.error(f"Error syncing live jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/saved", response_model=List[SavedJobOut])
def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve saved jobs for current user."""
    saved = (
        db.query(SavedJob)
        .filter(SavedJob.user_id == current_user.id)
        .order_by(SavedJob.saved_at.desc())
        .all()
    )

    result = []
    for s in saved:
        j = s.job
        job_out = (
            JobOut(
                id=j.id,
                external_id=j.external_id,
                title=j.title,
                company=j.company,
                location=j.location,
                description=j.description,
                salary_min=j.salary_min,
                salary_max=j.salary_max,
                salary_currency=j.salary_currency or "INR",
                job_type=j.job_type,
                work_mode=j.work_mode,
                experience_min=j.experience_min,
                experience_max=j.experience_max,
                education_required=j.education_required,
                original_url=j.original_url,
                posted_date=j.posted_date,
                collected_at=j.collected_at,
                is_seed_data=j.is_seed_data,
                source_name=j.source.name if j.source else None,
                skills=[{"skill_name": sk.skill_name, "is_required": sk.is_required} for sk in j.skills],
            )
            if j
            else None
        )
        result.append(
            SavedJobOut(
                id=s.id,
                job_id=s.job_id,
                status=s.status,
                notes=s.notes,
                saved_at=s.saved_at,
                job=job_out,
            )
        )
    return result


@router.get("/{job_id}", response_model=JobDetailOut)
def get_job_detail(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get single job details and log view interaction if user is logged in."""
    job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if current_user:
        interaction = ApplicationInteraction(
            user_id=current_user.id,
            job_id=job.id,
            interaction_type="viewed",
        )
        db.add(interaction)
        db.commit()

    return JobDetailOut(
        id=job.id,
        external_id=job.external_id,
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        responsibilities=job.responsibilities,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency or "INR",
        job_type=job.job_type,
        work_mode=job.work_mode,
        experience_min=job.experience_min,
        experience_max=job.experience_max,
        education_required=job.education_required,
        original_url=job.original_url,
        posted_date=job.posted_date,
        collected_at=job.collected_at,
        is_seed_data=job.is_seed_data,
        source_name=job.source.name if job.source else None,
        skills=[{"skill_name": s.skill_name, "is_required": s.is_required} for s in job.skills],
    )


@router.post("/{job_id}/save", response_model=SavedJobOut)
def save_job(
    job_id: int,
    body: SaveJobRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save or update saved status for a job."""
    job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    saved = (
        db.query(SavedJob)
        .filter(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id)
        .first()
    )
    if saved:
        saved.status = body.status
        saved.notes = body.notes
    else:
        saved = SavedJob(
            user_id=current_user.id,
            job_id=job_id,
            status=body.status,
            notes=body.notes,
        )
        db.add(saved)

    # Log interaction
    interaction = ApplicationInteraction(
        user_id=current_user.id,
        job_id=job_id,
        interaction_type="saved",
    )
    db.add(interaction)
    db.commit()
    db.refresh(saved)

    job_out = JobOut(
        id=job.id,
        external_id=job.external_id,
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency or "INR",
        job_type=job.job_type,
        work_mode=job.work_mode,
        experience_min=job.experience_min,
        experience_max=job.experience_max,
        education_required=job.education_required,
        original_url=job.original_url,
        posted_date=job.posted_date,
        collected_at=job.collected_at,
        is_seed_data=job.is_seed_data,
        source_name=job.source.name if job.source else None,
        skills=[{"skill_name": s.skill_name, "is_required": s.is_required} for s in job.skills],
    )
    return SavedJobOut(
        id=saved.id,
        job_id=saved.job_id,
        status=saved.status,
        notes=saved.notes,
        saved_at=saved.saved_at,
        job=job_out,
    )


@router.delete("/{job_id}/save")
def unsave_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a job from saved jobs."""
    saved = (
        db.query(SavedJob)
        .filter(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved job not found")

    db.delete(saved)
    db.commit()
    return {"message": "Job removed from saved list", "job_id": job_id}


@router.post("/{job_id}/interact")
def record_interaction(
    job_id: int,
    body: InteractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record candidate interaction with a job (view, apply click, dismiss)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    interaction = ApplicationInteraction(
        user_id=current_user.id,
        job_id=job_id,
        interaction_type=body.interaction_type,
    )
    db.add(interaction)
    db.commit()
    return {"status": "ok", "interaction_type": body.interaction_type, "job_id": job_id}


@router.get("/stats/summary")
def get_job_stats(db: Session = Depends(get_db)):
    """Aggregate statistics for jobs in system."""
    total_jobs = db.query(Job).filter(Job.is_active == True).count()
    remote_jobs = db.query(Job).filter(Job.is_active == True, Job.work_mode == "remote").count()
    hybrid_jobs = db.query(Job).filter(Job.is_active == True, Job.work_mode == "hybrid").count()
    onsite_jobs = db.query(Job).filter(Job.is_active == True, Job.work_mode == "onsite").count()

    top_skills_query = (
        db.query(JobSkill.skill_name, func.count(JobSkill.job_id).label("count"))
        .group_by(JobSkill.skill_name)
        .order_by(func.count(JobSkill.job_id).desc())
        .limit(10)
        .all()
    )
    top_skills = [{"skill": s[0], "count": s[1]} for s in top_skills_query]

    top_locations_query = (
        db.query(Job.location, func.count(Job.id).label("count"))
        .filter(Job.is_active == True, Job.location != None)
        .group_by(Job.location)
        .order_by(func.count(Job.id).desc())
        .limit(8)
        .all()
    )
    top_locations = [{"location": loc[0], "count": loc[1]} for loc in top_locations_query if loc[0]]

    return {
        "total_jobs": total_jobs,
        "remote_jobs": remote_jobs,
        "hybrid_jobs": hybrid_jobs,
        "onsite_jobs": onsite_jobs,
        "top_skills": top_skills,
        "top_locations": top_locations,
    }
