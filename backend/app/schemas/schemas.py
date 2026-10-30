"""
Pydantic v2 schemas for all API request/response models.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ══════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: Optional[str] = None
    is_admin: bool = False


class UserOut(BaseModel):
    id: int
    email: str
    is_active: bool
    is_admin: bool
    is_email_verified: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# OTP / Email-verification schemas
class SendOTPRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class MessageResponse(BaseModel):
    message: str


# ══════════════════════════════════════════════════════════════════════
# PROFILE
# ══════════════════════════════════════════════════════════════════════
class ProfileCreate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    experience_years: Optional[float] = 0.0
    experience_level: Optional[str] = None
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None


class ProfileOut(ProfileCreate):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PreferencesCreate(BaseModel):
    preferred_roles: Optional[List[str]] = []
    preferred_locations: Optional[List[str]] = []
    remote_preference: Optional[str] = "any"
    employment_type: Optional[str] = "any"
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None


class PreferencesOut(PreferencesCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════
# RESUME
# ══════════════════════════════════════════════════════════════════════
class ResumeOut(BaseModel):
    id: int
    user_id: int
    filename: str
    file_type: str
    file_size_bytes: Optional[int] = None
    status: str
    processed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeAnalysisOut(BaseModel):
    resume_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    total_experience_years: float = 0.0
    job_titles: List[str] = []
    certifications: List[str] = []
    projects: List[Any] = []
    summary: Optional[str] = None


class CandidateSkillOut(BaseModel):
    id: int
    skill_name: str
    skill_category: Optional[str] = None
    proficiency: Optional[str] = None
    source: str

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════
# JOBS
# ══════════════════════════════════════════════════════════════════════
class JobSkillOut(BaseModel):
    skill_name: str
    is_required: bool

    class Config:
        from_attributes = True


class JobOut(BaseModel):
    id: int
    external_id: Optional[str] = None
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "INR"
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    education_required: Optional[str] = None
    original_url: str
    posted_date: Optional[datetime] = None
    collected_at: Optional[datetime] = None
    is_seed_data: bool = False
    source_name: Optional[str] = None
    skills: List[JobSkillOut] = []

    class Config:
        from_attributes = True


class JobDetailOut(JobOut):
    responsibilities: Optional[str] = None


class JobSearchParams(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    work_mode: Optional[str] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    skills: Optional[List[str]] = None
    source: Optional[str] = None
    posted_after: Optional[datetime] = None
    sort_by: Optional[str] = "posted_date"   # posted_date/match_score/salary
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ══════════════════════════════════════════════════════════════════════
# RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════
class SkillGapOut(BaseModel):
    skill_name: str
    gap_type: str  # matching/partial/missing

    class Config:
        from_attributes = True


class RecommendationOut(BaseModel):
    id: int
    job_id: int
    overall_score: float
    skill_score: float
    semantic_score: float
    experience_score: float
    education_score: float
    preference_score: float
    explanation: Optional[Dict[str, Any]] = None
    computed_at: datetime
    job: Optional[JobOut] = None

    class Config:
        from_attributes = True


class RecommendationDetailOut(RecommendationOut):
    skill_gaps: List[SkillGapOut] = []
    job: Optional[JobDetailOut] = None


# ══════════════════════════════════════════════════════════════════════
# SAVED JOBS
# ══════════════════════════════════════════════════════════════════════
class SaveJobRequest(BaseModel):
    status: str = "saved"   # saved/interested/not_interested/applied
    notes: Optional[str] = None


class SavedJobOut(BaseModel):
    id: int
    job_id: int
    status: str
    notes: Optional[str] = None
    saved_at: datetime
    job: Optional[JobOut] = None

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════
# INTERACTIONS
# ══════════════════════════════════════════════════════════════════════
class InteractionRequest(BaseModel):
    job_id: Optional[int] = None
    interaction_type: str   # viewed/clicked_apply/saved/dismissed


# ══════════════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════════════
class JobSourceOut(BaseModel):
    id: int
    name: str
    source_type: str
    is_active: bool
    last_collected_at: Optional[datetime] = None
    jobs_collected: int
    error_count: int

    class Config:
        from_attributes = True


class AdminStatsOut(BaseModel):
    total_jobs: int
    active_jobs: int
    seed_jobs: int
    total_users: int
    total_recommendations: int
    duplicate_groups: int
    job_sources: int


# ══════════════════════════════════════════════════════════════════════
# PAGINATION
# ══════════════════════════════════════════════════════════════════════
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int
