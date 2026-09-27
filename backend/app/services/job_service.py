"""
Job Service – handles job collection, storage, and retrieval.
Orchestrates: source adapters → normalization → dedup → DB storage.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.ai.embeddings import (
    build_job_text,
    embedding_to_json,
    get_embedding,
    json_to_embedding,
)
from app.job_sources.api_source import (
    AdzunaSource,
    ArbeitnowSource,
    JobicySource,
    JoobleSource,
    RemotiveSource,
)
from app.job_sources.base_source import BaseJobSource, RawJob
from app.job_sources.scraper_source import ScraperSource
from app.job_sources.seed_source import SeedDataSource
from app.models import Job, JobDuplicate, JobSkill, JobSource
from app.services.duplicate_detector import (
    build_structured_key_map,
    check_exact_duplicate,
    check_semantic_duplicate,
    check_structured_duplicate,
)
from app.services.normalization import normalize_job
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── All registered source adapters ───────────────────────────────────
ALL_SOURCES: List[BaseJobSource] = [
    RemotiveSource(),
    ArbeitnowSource(),
    JobicySource(),
    AdzunaSource(),
    JoobleSource(),
    ScraperSource(),
    SeedDataSource(),
]


def get_or_create_source(db: Session, adapter: BaseJobSource) -> JobSource:
    """Get or create JobSource record for this adapter."""
    source = db.query(JobSource).filter(JobSource.name == adapter.name).first()
    if not source:
        source = JobSource(
            name=adapter.name,
            source_type=adapter.source_type,
            base_url=adapter.base_url,
            is_active=True,
        )
        db.add(source)
        db.commit()
        db.refresh(source)
    return source


def collect_and_store_jobs(db: Session, max_per_source: int = 100) -> Dict[str, Any]:
    """
    Main job collection orchestrator.
    Runs all available source adapters → normalize → dedup → store.
    Returns collection statistics.
    """
    stats = {"collected": 0, "stored": 0, "duplicates": 0, "errors": 0}

    # Load existing jobs for dedup comparison
    existing_jobs = db.query(Job).filter(Job.is_active == True).all()
    existing_dicts = [
        {
            "id": j.id,
            "external_id": j.external_id,
            "original_url": j.original_url,
            "company": j.company,
            "title": j.title,
            "location": j.location,
        }
        for j in existing_jobs
    ]
    structured_keys = build_structured_key_map(existing_dicts)

    # Load embeddings for semantic dedup (only recent jobs to avoid slow startup)
    recent_embeddings: List[Tuple[int, List]] = []
    for j in existing_jobs[-200:]:  # Only last 200 jobs for perf
        emb = json_to_embedding(j.embedding)
        if emb:
            recent_embeddings.append((j.id, emb))

    for adapter in ALL_SOURCES:
        if not adapter.is_available():
            continue

        source_record = get_or_create_source(db, adapter)
        logger.info(f"Collecting from: {adapter.name}")

        try:
            raw_jobs: List[RawJob] = adapter.collect(max_results=max_per_source)
            stats["collected"] += len(raw_jobs)

            for raw in raw_jobs:
                raw_dict = raw.to_dict()

                # Normalize
                try:
                    normalized = normalize_job(raw_dict)
                except Exception as e:
                    logger.error(f"Normalization error: {e}")
                    stats["errors"] += 1
                    continue

                # Dedup Level 1: Exact
                dup_id = check_exact_duplicate(
                    normalized.get("external_id"),
                    normalized.get("original_url", ""),
                    existing_dicts,
                )
                if dup_id:
                    _record_duplicate(db, dup_id, None, None, 1)
                    stats["duplicates"] += 1
                    continue

                # Dedup Level 2: Structured
                dup_id = check_structured_duplicate(
                    normalized.get("company", ""),
                    normalized.get("title", ""),
                    normalized.get("location", ""),
                    structured_keys,
                )
                if dup_id:
                    _record_duplicate(db, dup_id, None, None, 2)
                    stats["duplicates"] += 1
                    continue

                # Generate embedding for storage + semantic dedup
                job_text = build_job_text(normalized)
                embedding = get_embedding(job_text)
                embedding_json = embedding_to_json(embedding)

                # Dedup Level 3: Semantic
                if recent_embeddings and normalized.get("description"):
                    result = check_semantic_duplicate(
                        normalized.get("description", ""),
                        recent_embeddings,
                    )
                    if result:
                        dup_id, sim = result
                        _record_duplicate(db, dup_id, None, sim, 3)
                        stats["duplicates"] += 1
                        continue

                # Store new job
                skills = normalized.pop("required_skills", [])
                job = Job(
                    external_id=normalized.get("external_id"),
                    source_id=source_record.id,
                    title=normalized.get("title", ""),
                    company=normalized.get("company"),
                    location=normalized.get("location"),
                    description=normalized.get("description"),
                    responsibilities=normalized.get("responsibilities"),
                    salary_min=normalized.get("salary_min"),
                    salary_max=normalized.get("salary_max"),
                    salary_currency=normalized.get("salary_currency", "INR"),
                    job_type=normalized.get("job_type"),
                    work_mode=normalized.get("work_mode"),
                    experience_min=normalized.get("experience_min"),
                    experience_max=normalized.get("experience_max"),
                    education_required=normalized.get("education_required"),
                    original_url=normalized.get("original_url", "#"),
                    posted_date=normalized.get("posted_date"),
                    is_seed_data=normalized.get("is_seed_data", False),
                    embedding=embedding_json,
                    processed=True,
                )
                db.add(job)
                db.flush()

                # Add skills
                for skill_name in skills:
                    if skill_name:
                        skill = JobSkill(job_id=job.id, skill_name=skill_name, is_required=True)
                        db.add(skill)

                # Update dedup caches
                existing_dicts.append({
                    "id": job.id,
                    "external_id": job.external_id,
                    "original_url": job.original_url,
                    "company": job.company,
                    "title": job.title,
                    "location": job.location,
                })
                structured_key = f"{(job.company or '').lower()}|{(job.title or '').lower()}|{(job.location or '').lower()}"
                structured_keys[structured_key] = job.id
                recent_embeddings.append((job.id, embedding))

                stats["stored"] += 1

            db.commit()

            # Update source stats
            source_record.last_collected_at = datetime.now(timezone.utc)
            source_record.jobs_collected = (source_record.jobs_collected or 0) + stats["stored"]
            db.commit()

        except Exception as e:
            logger.error(f"Error collecting from {adapter.name}: {e}")
            source_record.error_count = (source_record.error_count or 0) + 1
            source_record.last_error = str(e)
            db.commit()
            stats["errors"] += 1

    logger.info(f"Job collection complete: {stats}")
    return stats


def _record_duplicate(db: Session, primary_id: int, duplicate_id: Optional[int], sim: Optional[float], level: int):
    """Record a duplicate pair in the database."""
    if duplicate_id and primary_id != duplicate_id:
        existing = db.query(JobDuplicate).filter(
            JobDuplicate.primary_job_id == primary_id,
            JobDuplicate.duplicate_job_id == duplicate_id,
        ).first()
        if not existing:
            dup = JobDuplicate(
                primary_job_id=primary_id,
                duplicate_job_id=duplicate_id,
                similarity_score=sim,
                detection_level=level,
            )
            db.add(dup)


def get_jobs_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    query: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    work_mode: Optional[str] = None,
    experience_min: Optional[float] = None,
    experience_max: Optional[float] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    skills: Optional[List[str]] = None,
    sort_by: str = "posted_date",
    real_only: Optional[bool] = None,
) -> Tuple[List[Job], int]:
    """Search and filter jobs with pagination."""
    q = db.query(Job).filter(Job.is_active == True)

    if real_only is True:
        q = q.filter(Job.is_seed_data == False)
    elif real_only is False:
        q = q.filter(Job.is_seed_data == True)

    if query:
        q = q.filter(
            or_(
                Job.title.ilike(f"%{query}%"),
                Job.company.ilike(f"%{query}%"),
                Job.description.ilike(f"%{query}%"),
            )
        )
    if location:
        q = q.filter(Job.location.ilike(f"%{location}%"))
    if job_type:
        q = q.filter(Job.job_type == job_type)
    if work_mode:
        q = q.filter(Job.work_mode == work_mode)
    if experience_min is not None:
        q = q.filter(or_(Job.experience_min == None, Job.experience_max >= experience_min))
    if experience_max is not None:
        q = q.filter(or_(Job.experience_max == None, Job.experience_min <= experience_max))
    if salary_min:
        q = q.filter(or_(Job.salary_max == None, Job.salary_max >= salary_min))
    if salary_max:
        q = q.filter(or_(Job.salary_min == None, Job.salary_min <= salary_max))

    if skills:
        from app.models import JobSkill as JS
        for skill in skills:
            q = q.filter(
                Job.id.in_(
                    db.query(JS.job_id).filter(JS.skill_name.ilike(f"%{skill}%"))
                )
            )

    total = q.count()

    if sort_by == "salary":
        q = q.order_by(Job.salary_max.desc().nullslast())
    else:
        q = q.order_by(Job.posted_date.desc().nullslast())

    offset = (page - 1) * page_size
    jobs = q.offset(offset).limit(page_size).all()
    return jobs, total
