"""
API package routers for JobPilot AI.
"""
from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.profile import router as profile_router
from app.api.recommendations import router as recommendations_router
from app.api.resume import router as resume_router
from app.api.skills import router as skills_router

__all__ = [
    "auth_router",
    "profile_router",
    "resume_router",
    "jobs_router",
    "recommendations_router",
    "skills_router",
    "admin_router",
]
