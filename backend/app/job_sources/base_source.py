"""
Base Job Source – abstract interface for all job data providers.
Every source adapter must implement collect() and return Job dicts
in the normalized schema.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class RawJob:
    """Normalized job schema returned by all source adapters."""
    external_id: Optional[str]
    title: str
    company: Optional[str]
    location: Optional[str]
    description: Optional[str]
    responsibilities: Optional[str]
    required_skills: List[str]
    experience_min: Optional[float]
    experience_max: Optional[float]
    education_required: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    salary_currency: str
    job_type: Optional[str]
    work_mode: Optional[str]
    posted_date: Optional[datetime]
    original_url: str
    source_name: str
    is_seed_data: bool = False
    collected_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "external_id": self.external_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "responsibilities": self.responsibilities,
            "required_skills": self.required_skills,
            "experience_min": self.experience_min,
            "experience_max": self.experience_max,
            "education_required": self.education_required,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "job_type": self.job_type,
            "work_mode": self.work_mode,
            "posted_date": self.posted_date,
            "original_url": self.original_url,
            "source_name": self.source_name,
            "is_seed_data": self.is_seed_data,
            "collected_at": self.collected_at,
        }


class BaseJobSource(ABC):
    """Abstract base class for all job source adapters."""

    name: str = "base"
    source_type: str = "base"  # api | scraper | seed
    base_url: str = ""

    @abstractmethod
    def collect(self, query: str = "", location: str = "", max_results: int = 50) -> List[RawJob]:
        """
        Collect jobs from this source.
        Must return a list of RawJob objects.
        Should handle errors gracefully and return empty list on failure.
        """
        ...

    def is_available(self) -> bool:
        """Check if this source is configured and available."""
        return True
