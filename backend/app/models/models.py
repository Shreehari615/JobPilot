"""
All SQLAlchemy ORM models for JobPilot AI.
Tables: users, profiles, user_preferences, resumes, candidate_skills,
        candidate_experiences, candidate_education, jobs, job_skills,
        job_sources, job_duplicates, recommendations, skill_gaps,
        saved_jobs, application_interactions
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


# ── Users ─────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    resumes = relationship("Resume", back_populates="user")
    candidate_skills = relationship("CandidateSkill", back_populates="user")
    candidate_experiences = relationship("CandidateExperience", back_populates="user")
    candidate_education = relationship("CandidateEducation", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    saved_jobs = relationship("SavedJob", back_populates="user")
    interactions = relationship("ApplicationInteraction", back_populates="user")


# ── Profiles ──────────────────────────────────────────────────────────
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True, index=True)
    bio = Column(Text, nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    experience_years = Column(Float, default=0.0)
    experience_level = Column(String(50), nullable=True)  # fresher/junior/mid/senior
    expected_salary_min = Column(Integer, nullable=True)
    expected_salary_max = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="profile")


# ── User Preferences ──────────────────────────────────────────────────
class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    preferred_roles = Column(Text, default="[]")       # JSON array
    preferred_locations = Column(Text, default="[]")   # JSON array
    remote_preference = Column(String(20), default="any")  # remote/hybrid/onsite/any
    employment_type = Column(String(20), default="any")    # full-time/part-time/contract/any
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="preferences")

    @property
    def preferred_roles_list(self):
        return json.loads(self.preferred_roles or "[]")

    @property
    def preferred_locations_list(self):
        return json.loads(self.preferred_locations or "[]")


# ── Resumes ───────────────────────────────────────────────────────────
class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)   # UUID-based safe name
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)          # pdf | docx
    file_size_bytes = Column(Integer, nullable=True)
    raw_text = Column(Text, nullable=True)
    status = Column(String(20), default="pending")          # pending|processing|done|error
    analysis_result = Column(Text, nullable=True)           # JSON blob
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="resumes")


# ── Candidate Skills ──────────────────────────────────────────────────
class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    skill_category = Column(String(50), nullable=True)      # languages/web/ai_ml/databases/cloud/other
    proficiency = Column(String(20), nullable=True)         # beginner/intermediate/advanced/expert
    source = Column(String(20), default="resume")           # resume/manual
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "skill_name", name="uq_user_skill"),
        Index("ix_candidate_skills_user_skill", "user_id", "skill_name"),
    )

    user = relationship("User", back_populates="candidate_skills")


# ── Candidate Experience ──────────────────────────────────────────────
class CandidateExperience(Base):
    __tablename__ = "candidate_experiences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    start_date = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    duration_months = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="candidate_experiences")


# ── Candidate Education ───────────────────────────────────────────────
class CandidateEducation(Base):
    __tablename__ = "candidate_education"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    degree = Column(String(100), nullable=True)
    field_of_study = Column(String(255), nullable=True)
    institution = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    grade = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="candidate_education")


# ── Job Sources ───────────────────────────────────────────────────────
class JobSource(Base):
    __tablename__ = "job_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    source_type = Column(String(20), nullable=False)        # api/scraper/seed
    base_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    last_collected_at = Column(DateTime(timezone=True), nullable=True)
    jobs_collected = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    jobs = relationship("Job", back_populates="source")


# ── Jobs ──────────────────────────────────────────────────────────────
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), nullable=True)
    source_id = Column(Integer, ForeignKey("job_sources.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True, index=True)
    location = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="INR")
    job_type = Column(String(30), nullable=True, index=True)    # full-time/part-time/contract/internship
    work_mode = Column(String(20), nullable=True)               # remote/hybrid/onsite
    experience_min = Column(Float, nullable=True)
    experience_max = Column(Float, nullable=True)
    education_required = Column(String(100), nullable=True)
    original_url = Column(String(2000), nullable=False)
    posted_date = Column(DateTime(timezone=True), nullable=True, index=True)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    is_seed_data = Column(Boolean, default=False)               # development/demo flag
    embedding = Column(Text, nullable=True)                     # JSON-encoded vector
    processed = Column(Boolean, default=False)

    __table_args__ = (
        Index("ix_jobs_company_title_location", "company", "title", "location"),
        Index("ix_jobs_source_external", "source_id", "external_id"),
    )

    source = relationship("JobSource", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="job")
    saved_by = relationship("SavedJob", back_populates="job")
    duplicate_primary = relationship("JobDuplicate", foreign_keys="JobDuplicate.primary_job_id", back_populates="primary_job")
    duplicate_copy = relationship("JobDuplicate", foreign_keys="JobDuplicate.duplicate_job_id", back_populates="duplicate_job")


# ── Job Skills ────────────────────────────────────────────────────────
class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    is_required = Column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("job_id", "skill_name", name="uq_job_skill"),)

    job = relationship("Job", back_populates="skills")


# ── Job Duplicates ────────────────────────────────────────────────────
class JobDuplicate(Base):
    __tablename__ = "job_duplicates"

    id = Column(Integer, primary_key=True, index=True)
    primary_job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    duplicate_job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity_score = Column(Float, nullable=True)
    detection_level = Column(Integer, nullable=False)   # 1/2/3
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("primary_job_id", "duplicate_job_id", name="uq_duplicate_pair"),)

    primary_job = relationship("Job", foreign_keys=[primary_job_id], back_populates="duplicate_primary")
    duplicate_job = relationship("Job", foreign_keys=[duplicate_job_id], back_populates="duplicate_copy")


# ── Recommendations ───────────────────────────────────────────────────
class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)
    skill_score = Column(Float, default=0.0)
    semantic_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    preference_score = Column(Float, default=0.0)
    explanation = Column(Text, nullable=True)   # JSON blob
    computed_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_recommendation"),
        Index("ix_recommendations_user_score", "user_id", "overall_score"),
    )

    user = relationship("User", back_populates="recommendations")
    job = relationship("Job", back_populates="recommendations")


# ── Skill Gaps ────────────────────────────────────────────────────────
class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    gap_type = Column(String(20), nullable=False)   # matching/partial/missing

    __table_args__ = (
        Index("ix_skill_gaps_user_job", "user_id", "job_id"),
        UniqueConstraint("user_id", "job_id", "skill_name", name="uq_skill_gap"),
    )


# ── Saved Jobs ────────────────────────────────────────────────────────
class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="saved")    # saved/interested/not_interested/applied
    notes = Column(Text, nullable=True)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_saved_job"),)

    user = relationship("User", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by")


# ── Application Interactions ──────────────────────────────────────────
class ApplicationInteraction(Base):
    __tablename__ = "application_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type = Column(String(30), nullable=False)   # viewed/clicked_apply/saved/dismissed
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_interactions_user_job", "user_id", "job_id"),)

    user = relationship("User", back_populates="interactions")
