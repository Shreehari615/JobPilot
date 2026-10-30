"""
JobPilot AI – Main FastAPI Application Entrypoint.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import (
    admin_router,
    auth_router,
    jobs_router,
    profile_router,
    recommendations_router,
    resume_router,
    skills_router,
)
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import Job
from app.services.job_service import collect_and_store_jobs
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Ensure tables exist
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

    # Ensure upload directory exists
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)

    # Auto-seed initial jobs or collect real jobs if database has no active real jobs
    db = SessionLocal()
    try:
        real_job_count = db.query(Job).filter(Job.is_seed_data == False, Job.is_active == True).count()
        if real_job_count < 10:
            logger.info(f"Database only has {real_job_count} real jobs. Collecting live real jobs...")
            collect_and_store_jobs(db, max_per_source=30)
            new_count = db.query(Job).count()
            logger.info(f"Job collection completed. {new_count} total jobs in database.")
        else:
            logger.info(f"Database already has {real_job_count} active real jobs.")
    except Exception as e:
        logger.error(f"Error during job initialization: {e}")
    finally:
        db.close()

    yield
    logger.info("Shutting down JobPilot AI application.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Unified AI Job Discovery & Application Assistant API.\n"
        "Features resume NLP, multi-factor job matching, skill gap analysis, "
        "and multi-source job aggregation."
    ),
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────────────
origins = list(settings.CORS_ORIGINS) if isinstance(settings.CORS_ORIGINS, list) else []
for o in [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "https://getjobpilot.vercel.app",
]:
    if o not in origins:
        origins.append(o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ── Include Routers (under /api/v1 and /api) ──────────────────────────
for prefix in ["/api/v1", "/api"]:
    app.include_router(auth_router, prefix=prefix)
    app.include_router(profile_router, prefix=prefix)
    app.include_router(resume_router, prefix=f"{prefix}/resume")
    app.include_router(resume_router, prefix=f"{prefix}/resumes")
    app.include_router(jobs_router, prefix=prefix)
    app.include_router(recommendations_router, prefix=prefix)
    app.include_router(skills_router, prefix=prefix)
    app.include_router(admin_router, prefix=prefix)

# ── Static Uploads Mount ──────────────────────────────────────────────
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

@app.get("/", tags=["Root"])
@app.get("/api", tags=["Root"])
@app.get("/api/v1", tags=["Root"])
def root():
    """Root entry point."""
    return {
        "message": "Welcome to JobPilot AI Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api_v1_health": "/api/v1/health",
        "endpoints": {
            "jobs": "/api/v1/jobs",
            "auth": "/api/v1/auth",
            "profile": "/api/v1/profile",
            "resume": "/api/v1/resume",
            "recommendations": "/api/v1/recommendations",
            "skills": "/api/v1/skills",
            "admin": "/api/v1/admin"
        }
    }


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
def health_check():
    """System health check endpoint."""
    from app.services.llm_service import llm_service
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "embedding_model": settings.EMBEDDING_MODEL,
        "llm": llm_service.get_status(),
    }
