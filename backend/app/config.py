"""
JobPilot AI – Application Configuration
All settings are loaded from environment variables (.env file).
Never hard-code secrets here.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────────────
    APP_NAME: str = "JobPilot AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ── Database ──────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/jobpilot"

    # ── Security ──────────────────────────────────────────────────────
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24h

    # ── CORS ──────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                return json.loads(v)
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    # ── File Upload ───────────────────────────────────────────────────
    MAX_RESUME_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads/resumes"

    # ── AI / LLM ──────────────────────────────────────────────────────
    LLM_PROVIDER: str = "local"  # local | openai | gemini
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ── Job Source APIs ───────────────────────────────────────────────
    ADZUNA_APP_ID: str = ""
    ADZUNA_APP_KEY: str = ""
    ADZUNA_COUNTRY: str = "in"  # ISO 3166-1 alpha-2: gb, us, au, in, de, fr, ca, sg, etc.
    JOOBLE_API_KEY: str = ""

    # ── Matching Weights ─────────────────────────────────────────────
    MATCH_WEIGHT_SKILLS: float = 0.35
    MATCH_WEIGHT_SEMANTIC: float = 0.30
    MATCH_WEIGHT_EXPERIENCE: float = 0.15
    MATCH_WEIGHT_EDUCATION: float = 0.10
    MATCH_WEIGHT_PREFERENCES: float = 0.10

    # ── Deduplication ─────────────────────────────────────────────────
    DEDUP_SEMANTIC_THRESHOLD: float = 0.85

    # ── Seed Data ─────────────────────────────────────────────────────
    SEED_DEMO_DATA: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def match_weights(self) -> dict:
        """Configurable matching weights – never hard-coded in business logic."""
        return {
            "skills": self.MATCH_WEIGHT_SKILLS,
            "semantic": self.MATCH_WEIGHT_SEMANTIC,
            "experience": self.MATCH_WEIGHT_EXPERIENCE,
            "education": self.MATCH_WEIGHT_EDUCATION,
            "preferences": self.MATCH_WEIGHT_PREFERENCES,
        }

    @property
    def max_resume_bytes(self) -> int:
        return self.MAX_RESUME_SIZE_MB * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    return Settings()
