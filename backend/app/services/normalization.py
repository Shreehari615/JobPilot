"""
Job data cleaning and normalization pipeline.

Every collected job passes through this pipeline before storage:
  whitespace/HTML strip → encoding fix → field normalization →
  skill normalization → date normalization → URL preservation
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.ai.skill_taxonomy import extract_skills_from_text, normalize_skill
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── HTML stripping ────────────────────────────────────────────────────
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")

LOCATION_NORMALIZATIONS = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "blr": "Bengaluru",
    "bombay": "Mumbai",
    "delhi": "Delhi NCR",
    "new delhi": "Delhi NCR",
    "ncr": "Delhi NCR",
    "gurgaon": "Delhi NCR",
    "noida": "Delhi NCR",
    "hyderabad": "Hyderabad",
    "hyd": "Hyderabad",
    "pune": "Pune",
    "chennai": "Chennai",
    "madras": "Chennai",
    "kochi": "Kochi",
    "cochin": "Kochi",
    "mysore": "Mysuru",
    "mysuru": "Mysuru",
    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
}

JOB_TYPE_NORMALIZATIONS = {
    "fulltime": "full-time", "full time": "full-time",
    "parttime": "part-time", "part time": "part-time",
    "contractual": "contract", "freelance": "contract",
    "internship": "internship", "intern": "internship",
    "temporary": "contract",
}

WORK_MODE_NORMALIZATIONS = {
    "work from home": "remote", "wfh": "remote",
    "fully remote": "remote",
    "work from office": "onsite", "wfo": "onsite",
    "in-office": "onsite", "in office": "onsite",
    "hybrid": "hybrid", "partial remote": "hybrid",
}


def _to_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, (list, tuple)):
        return " ".join(str(x) for x in val if x)
    return str(val)


def strip_html(text: Optional[Any]) -> str:
    s = _to_str(text)
    if not s:
        return ""
    s = _HTML_TAG_RE.sub(" ", s)
    s = _WHITESPACE_RE.sub(" ", s)
    return s.strip()


def normalize_location(location: Optional[Any]) -> Optional[str]:
    loc_str = _to_str(location)
    if not loc_str:
        return None
    loc_lower = loc_str.lower().strip()
    for alias, canonical in LOCATION_NORMALIZATIONS.items():
        if alias in loc_lower:
            # Preserve remote/hybrid qualifiers
            if "remote" in loc_lower:
                return f"{canonical} (Remote)"
            return canonical
    return loc_str.strip().title()


def normalize_job_type(job_type: Optional[Any]) -> Optional[str]:
    jt_str = _to_str(job_type)
    if not jt_str:
        return None
    jt_lower = jt_str.lower().strip()
    for alias, canonical in JOB_TYPE_NORMALIZATIONS.items():
        if alias in jt_lower:
            return canonical
    return jt_str.lower().strip()


def normalize_work_mode(text: Optional[Any]) -> Optional[str]:
    t_str = _to_str(text)
    if not t_str:
        return None
    t_lower = t_str.lower().strip()
    for alias, canonical in WORK_MODE_NORMALIZATIONS.items():
        if alias in t_lower:
            return canonical
    if "remote" in t_lower:
        return "remote"
    if "hybrid" in t_lower:
        return "hybrid"
    if "onsite" in t_lower or "office" in t_lower:
        return "onsite"
    return None


def normalize_company(company: Optional[str]) -> Optional[str]:
    if not company:
        return None
    company = company.strip()
    # Remove common suffixes for normalization
    company = re.sub(r"\s+(pvt\.?\s*ltd\.?|private\s+limited|limited|inc\.?|llc|corp\.?)$",
                     "", company, flags=re.IGNORECASE)
    return company.strip()


def normalize_title(title: Optional[str]) -> Optional[str]:
    if not title:
        return None
    title = title.strip()
    replacements = {
        r"\bSr\.?\b": "Senior",
        r"\bJr\.?\b": "Junior",
        r"\bDev\b": "Developer",
        r"\bEng\b": "Engineer",
        r"\bMgr\b": "Manager",
        r"\bSWE\b": "Software Engineer",
        r"\bSDE\b": "Software Development Engineer",
    }
    for pattern, full in replacements.items():
        title = re.sub(pattern, full, title)
    return title.strip()


def extract_salary(salary_text: Optional[str]) -> Dict[str, Optional[int]]:
    """Parse salary range from text like '₹8-12 LPA' or '8,00,000 - 12,00,000'."""
    result = {"min": None, "max": None, "currency": "INR"}
    if not salary_text:
        return result

    text = salary_text.replace(",", "").replace("₹", "").replace("$", "")
    # LPA pattern (lakhs per annum)
    lpa_match = re.search(r"(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)\s*lpa", text, re.IGNORECASE)
    if lpa_match:
        result["min"] = int(float(lpa_match.group(1)) * 100000)
        result["max"] = int(float(lpa_match.group(2)) * 100000)
        return result

    single_lpa = re.search(r"(\d+(?:\.\d+)?)\s*lpa", text, re.IGNORECASE)
    if single_lpa:
        val = int(float(single_lpa.group(1)) * 100000)
        result["min"] = val
        result["max"] = val
        return result

    # Raw number range
    range_match = re.search(r"(\d{4,})\s*[-–to]+\s*(\d{4,})", text)
    if range_match:
        result["min"] = int(range_match.group(1))
        result["max"] = int(range_match.group(2))

    return result


def parse_experience_range(exp_text: Optional[str]) -> Dict[str, Optional[float]]:
    """Parse experience requirement like '2-5 years' or 'Minimum 3 years'."""
    result = {"min": None, "max": None}
    if not exp_text:
        return result

    range_match = re.search(r"(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", exp_text, re.IGNORECASE)
    if range_match:
        result["min"] = float(range_match.group(1))
        result["max"] = float(range_match.group(2))
        return result

    single_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", exp_text, re.IGNORECASE)
    if single_match:
        val = float(single_match.group(1))
        result["min"] = val
        result["max"] = val + 3.0

    return result


def normalize_job(raw_job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full cleaning and normalization pipeline for a raw job dict.
    Preserves the original_url at all times.
    """
    if hasattr(raw_job, "to_dict"):
        job = raw_job.to_dict()
    else:
        job = dict(raw_job)

    # Text fields
    job["title"] = normalize_title(strip_html(job.get("title")))
    job["company"] = normalize_company(strip_html(job.get("company")))
    job["description"] = strip_html(job.get("description"))
    job["responsibilities"] = strip_html(job.get("responsibilities"))

    # Location
    job["location"] = normalize_location(job.get("location"))
    if not job.get("work_mode"):
        job["work_mode"] = normalize_work_mode(job.get("description", ""))
    else:
        job["work_mode"] = normalize_work_mode(job.get("work_mode"))

    # Job type
    job["job_type"] = normalize_job_type(job.get("job_type"))

    # Salary
    if "salary_text" in job:
        sal = extract_salary(job.pop("salary_text"))
        job.setdefault("salary_min", sal["min"])
        job.setdefault("salary_max", sal["max"])

    # Experience
    if "experience_text" in job:
        exp = parse_experience_range(job.pop("experience_text"))
        job.setdefault("experience_min", exp["min"])
        job.setdefault("experience_max", exp["max"])

    # Skills: extract from description if not already provided
    if not job.get("required_skills") and job.get("description"):
        job["required_skills"] = extract_skills_from_text(job["description"])

    # Normalize skill names
    if job.get("required_skills"):
        normalized = []
        for s in job["required_skills"]:
            n = normalize_skill(s)
            normalized.append(n if n else s)
        job["required_skills"] = list(set(normalized))
    job["skills"] = job.get("required_skills", [])

    # Date normalization
    if job.get("posted_date") and isinstance(job["posted_date"], str):
        try:
            from dateutil import parser as dateparser
            job["posted_date"] = dateparser.parse(job["posted_date"])
        except Exception:
            job["posted_date"] = None

    # Ensure original_url is always present
    if not job.get("original_url"):
        logger.warning(f"Job missing original_url: {job.get('title')}")
        job["original_url"] = "#"

    return job
