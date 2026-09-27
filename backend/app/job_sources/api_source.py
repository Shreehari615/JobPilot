"""
API-based job source adapters.
Each adapter reads credentials from environment variables.
An adapter can be enabled/disabled without changing other code.
"""
from __future__ import annotations

import time
from datetime import datetime
from typing import List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.job_sources.base_source import BaseJobSource, RawJob
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AdzunaSource(BaseJobSource):
    """
    Adzuna Job Search API adapter.
    Free tier: https://developer.adzuna.com/
    Requires: ADZUNA_APP_ID, ADZUNA_APP_KEY env vars.
    Optional: ADZUNA_COUNTRY (ISO 3166-1 alpha-2, default: 'in' for India).
    Supported countries: gb, us, au, at, be, br, ca, de, fr, in, mx, nl, nz, pl, ru, sg, za.
    """

    name = "adzuna"
    source_type = "api"
    base_url = "https://api.adzuna.com/v1/api/jobs"

    # Adzuna-supported country codes
    SUPPORTED_COUNTRIES = {
        "gb", "us", "au", "at", "be", "br", "ca", "de",
        "fr", "in", "mx", "nl", "nz", "pl", "ru", "sg", "za",
    }

    def _get_country(self) -> str:
        """Return the configured Adzuna country code (default: 'in')."""
        import os
        country = os.environ.get("ADZUNA_COUNTRY", "in").lower().strip()
        return country if country in self.SUPPORTED_COUNTRIES else "in"

    def is_available(self) -> bool:
        from app.config import get_settings
        s = get_settings()
        return bool(s.ADZUNA_APP_ID and s.ADZUNA_APP_KEY)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch_page(self, app_id: str, app_key: str, query: str, location: str, page: int) -> dict:
        country = self._get_country()
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": 20,
            "what": query or "software engineer",
            "where": location or "",
            "content-type": "application/json",
        }
        # Page is part of the URL path, not a query param
        url = f"{self.base_url}/{country}/search/{page}"
        with httpx.Client(timeout=15) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    def collect(self, query: str = "", location: str = "", max_results: int = 50) -> List[RawJob]:
        from app.config import get_settings
        s = get_settings()

        if not self.is_available():
            logger.info("Adzuna API not configured, skipping")
            return []

        country = self._get_country()
        # Determine salary currency based on country
        currency_map = {
            "gb": "GBP", "us": "USD", "au": "AUD", "ca": "CAD",
            "de": "EUR", "fr": "EUR", "nl": "EUR", "at": "EUR",
            "be": "EUR", "in": "INR", "br": "BRL", "mx": "MXN",
            "sg": "SGD", "nz": "NZD", "za": "ZAR", "pl": "PLN",
            "ru": "RUB",
        }
        salary_currency = currency_map.get(country, "USD")

        jobs: List[RawJob] = []
        # Calculate exact number of pages needed (no over-fetching)
        pages_needed = max(1, (max_results + 19) // 20)

        for page in range(1, pages_needed + 1):
            try:
                data = self._fetch_page(s.ADZUNA_APP_ID, s.ADZUNA_APP_KEY, query, location, page)
                results = data.get("results", [])
                if not results:
                    logger.info(f"Adzuna: no results on page {page}, stopping early")
                    break

                for r in results:
                    # Safely coerce salary fields to int
                    raw_sal_min = r.get("salary_min")
                    raw_sal_max = r.get("salary_max")
                    try:
                        sal_min = int(float(raw_sal_min)) if raw_sal_min is not None else None
                    except (ValueError, TypeError):
                        sal_min = None
                    try:
                        sal_max = int(float(raw_sal_max)) if raw_sal_max is not None else None
                    except (ValueError, TypeError):
                        sal_max = None

                    # Parse posted date safely
                    posted_date = None
                    created = r.get("created")
                    if created:
                        try:
                            # Adzuna format: "2026-09-20T00:00:00Z"
                            posted_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        except (ValueError, AttributeError):
                            posted_date = None

                    # Infer work_mode from title/description heuristic
                    title_lower = (r.get("title") or "").lower()
                    desc_lower = (r.get("description") or "").lower()
                    if "remote" in title_lower or "remote" in desc_lower:
                        work_mode = "remote"
                    elif "hybrid" in title_lower or "hybrid" in desc_lower:
                        work_mode = "hybrid"
                    else:
                        work_mode = None

                    job = RawJob(
                        external_id=str(r.get("id")) if r.get("id") else None,
                        title=r.get("title", "").strip(),
                        company=(r.get("company") or {}).get("display_name"),
                        location=(r.get("location") or {}).get("display_name"),
                        description=r.get("description"),
                        responsibilities=None,
                        required_skills=[],   # Adzuna doesn't provide structured skills
                        experience_min=None,
                        experience_max=None,
                        education_required=None,
                        salary_min=sal_min,
                        salary_max=sal_max,
                        salary_currency=salary_currency,
                        job_type=r.get("contract_time"),
                        work_mode=work_mode,
                        posted_date=posted_date,
                        original_url=r.get("redirect_url", ""),
                        source_name=self.name,
                        is_seed_data=False,
                    )
                    jobs.append(job)

                if len(jobs) >= max_results:
                    break
                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                logger.error(f"Adzuna API error on page {page}: {e}")
                break

        logger.info(f"Adzuna: collected {len(jobs)} jobs (country={country})")
        return jobs[:max_results]


class JoobleSource(BaseJobSource):
    """
    Jooble API adapter.
    Free tier: https://jooble.org/api/about
    Requires: JOOBLE_API_KEY env var.
    """

    name = "jooble"
    source_type = "api"
    base_url = "https://jooble.org/api"

    def is_available(self) -> bool:
        from app.config import get_settings
        return bool(get_settings().JOOBLE_API_KEY)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch(self, api_key: str, keywords: str, location: str, page: int) -> dict:
        url = f"{self.base_url}/{api_key}"
        payload = {"keywords": keywords, "location": location, "page": page}
        with httpx.Client(timeout=15) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    def collect(self, query: str = "", location: str = "", max_results: int = 50) -> List[RawJob]:
        from app.config import get_settings
        s = get_settings()

        if not self.is_available():
            logger.info("Jooble API not configured, skipping")
            return []

        jobs = []
        try:
            data = self._fetch(s.JOOBLE_API_KEY, query or "software engineer", location or "India", 1)
            results = data.get("jobs", [])
            for r in results[:max_results]:
                job = RawJob(
                    external_id=r.get("id"),
                    title=r.get("title", ""),
                    company=r.get("company"),
                    location=r.get("location"),
                    description=r.get("snippet"),
                    responsibilities=None,
                    required_skills=[],
                    experience_min=None,
                    experience_max=None,
                    education_required=None,
                    salary_min=None,
                    salary_max=None,
                    salary_currency="INR",
                    job_type=r.get("type"),
                    work_mode=None,
                    posted_date=datetime.fromisoformat(r["updated"]) if r.get("updated") else None,
                    original_url=r.get("link", ""),
                    source_name=self.name,
                    is_seed_data=False,
                )
                jobs.append(job)
        except Exception as e:
            logger.error(f"Jooble API error: {e}")

        logger.info(f"Jooble: collected {len(jobs)} jobs")
        return jobs


class RemotiveSource(BaseJobSource):
    """
    Remotive Public Job API adapter.
    Free open API, no key required: https://remotive.com/api/remote-jobs
    Provides real live active tech & remote jobs with direct application URLs.
    """

    name = "remotive"
    source_type = "api"
    base_url = "https://remotive.com/api/remote-jobs"

    def is_available(self) -> bool:
        return True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch(self, category: str = "", limit: int = 50) -> dict:
        params = {"limit": limit}
        if category:
            params["category"] = category
        with httpx.Client(timeout=20) as client:
            response = client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()

    def collect(self, query: str = "", location: str = "", max_results: int = 50) -> List[RawJob]:
        jobs = []
        try:
            # First attempt software-dev category, then general if needed
            data = self._fetch(category="software-dev", limit=max_results)
            raw_items = data.get("jobs", [])
            if not raw_items:
                data = self._fetch(limit=max_results)
                raw_items = data.get("jobs", [])

            for r in raw_items[:max_results]:
                posted = None
                pub_date = r.get("publication_date")
                if pub_date:
                    try:
                        posted = datetime.fromisoformat(pub_date)
                    except Exception:
                        posted = None

                job = RawJob(
                    external_id=str(r.get("id")),
                    title=r.get("title", "").strip(),
                    company=r.get("company_name", "").strip(),
                    location=r.get("candidate_required_location") or "Remote",
                    description=r.get("description", ""),
                    responsibilities=None,
                    required_skills=r.get("tags") or [],
                    experience_min=None,
                    experience_max=None,
                    education_required=None,
                    salary_min=None,
                    salary_max=None,
                    salary_currency="USD",
                    job_type=r.get("job_type") or "full-time",
                    work_mode="remote",
                    posted_date=posted,
                    original_url=r.get("url", ""),
                    source_name=self.name,
                    is_seed_data=False,
                )
                jobs.append(job)
        except Exception as e:
            logger.error(f"Remotive API error: {e}")

        logger.info(f"Remotive: collected {len(jobs)} jobs")
        return jobs


class ArbeitnowSource(BaseJobSource):
    """
    Arbeitnow Job Board API adapter.
    Free open API, no key required: https://www.arbeitnow.com/api/job-board-api
    Provides real live jobs with authentic company application URLs.
    """

    name = "arbeitnow"
    source_type = "api"
    base_url = "https://www.arbeitnow.com/api/job-board-api"

    def is_available(self) -> bool:
        return True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch(self) -> dict:
        with httpx.Client(timeout=20) as client:
            response = client.get(self.base_url)
            response.raise_for_status()
            return response.json()

    def collect(self, query: str = "", location: str = "", max_results: int = 50) -> List[RawJob]:
        jobs = []
        try:
            data = self._fetch()
            raw_items = data.get("data", [])
            for r in raw_items[:max_results]:
                posted = None
                created_val = r.get("created_at")
                if isinstance(created_val, (int, float)):
                    try:
                        posted = datetime.fromtimestamp(created_val, timezone.utc)
                    except Exception:
                        posted = None
                elif isinstance(created_val, str):
                    try:
                        posted = datetime.fromisoformat(created_val)
                    except Exception:
                        posted = None

                job_types = r.get("job_types") or []
                job_type = job_types[0] if isinstance(job_types, list) and job_types else "full-time"

                job = RawJob(
                    external_id=str(r.get("slug") or r.get("id")),
                    title=r.get("title", "").strip(),
                    company=r.get("company_name", "").strip(),
                    location=r.get("location") or "Worldwide",
                    description=r.get("description", ""),
                    responsibilities=None,
                    required_skills=r.get("tags") or [],
                    experience_min=None,
                    experience_max=None,
                    education_required=None,
                    salary_min=None,
                    salary_max=None,
                    salary_currency="USD",
                    job_type=job_type,
                    work_mode="remote" if r.get("remote") else "onsite",
                    posted_date=posted,
                    original_url=r.get("url", ""),
                    source_name=self.name,
                    is_seed_data=False,
                )
                jobs.append(job)
        except Exception as e:
            logger.error(f"Arbeitnow API error: {e}")

        logger.info(f"Arbeitnow: collected {len(jobs)} jobs")
        return jobs


class JobicySource(BaseJobSource):
    """
    Jobicy Public Remote Jobs API adapter.
    Free open API: https://jobicy.com/api/v2/remote-jobs
    Provides active verified remote positions.
    """

    name = "jobicy"
    source_type = "api"
    base_url = "https://jobicy.com/api/v2/remote-jobs"

    def is_available(self) -> bool:
        return True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch(self, count: int = 50) -> dict:
        with httpx.Client(timeout=20) as client:
            response = client.get(self.base_url, params={"count": count})
            response.raise_for_status()
            return response.json()

    def collect(self, query: str = "", location: str = "", max_results: int = 50) -> List[RawJob]:
        jobs = []
        try:
            data = self._fetch(count=max_results)
            raw_items = data.get("jobs", [])
            for r in raw_items[:max_results]:
                posted = None
                pub = r.get("pubDate")
                if pub:
                    try:
                        posted = datetime.fromisoformat(pub)
                    except Exception:
                        posted = None

                skills = []
                industry = r.get("jobIndustry")
                if isinstance(industry, list):
                    skills.extend(industry)
                elif isinstance(industry, str) and industry:
                    skills.append(industry)

                job = RawJob(
                    external_id=str(r.get("id")),
                    title=r.get("jobTitle", "").strip(),
                    company=r.get("companyName", "").strip(),
                    location=r.get("jobGeo") or "Remote",
                    description=r.get("jobExcerpt") or r.get("jobDescription") or "",
                    responsibilities=None,
                    required_skills=skills,
                    experience_min=None,
                    experience_max=None,
                    education_required=None,
                    salary_min=None,
                    salary_max=None,
                    salary_currency="USD",
                    job_type=r.get("jobType") or "full-time",
                    work_mode="remote",
                    posted_date=posted,
                    original_url=r.get("url", ""),
                    source_name=self.name,
                    is_seed_data=False,
                )
                jobs.append(job)
        except Exception as e:
            logger.error(f"Jobicy API error: {e}")

        logger.info(f"Jobicy: collected {len(jobs)} jobs")
        return jobs
