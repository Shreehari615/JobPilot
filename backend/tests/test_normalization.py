"""
Unit tests for Job Normalization & Cleaning Pipeline.
"""
from app.job_sources.base_source import RawJob
from app.services.normalization import (
    normalize_job,
    normalize_location,
    normalize_work_mode,
    strip_html,
)


def test_strip_html():
    raw_html = "<p>We are hiring! <b>Python</b> &amp; <i>FastAPI</i></p><script>alert(1)</script>"
    cleaned = strip_html(raw_html)
    assert "<p>" not in cleaned
    assert "<b>" not in cleaned


def test_normalize_location():
    assert normalize_location("Bangalore") == "Bengaluru"
    assert normalize_location("Bombay") == "Mumbai"
    assert normalize_location("Pune") == "Pune"


def test_normalize_work_mode():
    assert normalize_work_mode("Work From Home") == "remote"
    assert normalize_work_mode("Hybrid") == "hybrid"
    assert normalize_work_mode("Work From Office") == "onsite"


def test_normalize_job_pipeline():
    raw = RawJob(
        external_id="ADZ-998877",
        title="  Senior Software Engineer - Python ",
        company=" Acme Tech Solutions ",
        location=" Bangalore ",
        description="<p>Must know Python, Docker, and PostgreSQL.</p>",
        responsibilities=None,
        required_skills=["Python", "Docker", "PostgreSQL"],
        experience_min=2.0,
        experience_max=5.0,
        education_required="B.Tech",
        salary_min=1500000,
        salary_max=2500000,
        salary_currency="INR",
        job_type="Full Time",
        work_mode="hybrid",
        posted_date=None,
        original_url="https://example.com/jobs/998877",
        source_name="adzuna",
    )

    clean = normalize_job(raw)
    assert clean["title"] == "Senior Software Engineer - Python"
    assert clean["company"] == "Acme Tech Solutions"
    assert clean["location"] == "Bengaluru"
    assert "<p>" not in clean["description"]
    assert "Python" in clean["skills"]
