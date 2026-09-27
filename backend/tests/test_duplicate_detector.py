"""
Unit tests for 3-level Duplicate Detector.
"""
from app.services.duplicate_detector import (
    build_structured_key_map,
    check_exact_duplicate,
    check_structured_duplicate,
)


def test_exact_duplicate():
    existing_jobs = [
        {"id": 1, "external_id": "JOB-101", "original_url": "https://example.com/jobs/101"},
        {"id": 2, "external_id": "JOB-102", "original_url": "https://example.com/jobs/102"},
    ]

    # Matching external ID
    dup_id = check_exact_duplicate("JOB-101", "https://other.com/job", existing_jobs)
    assert dup_id == 1

    # Matching URL
    dup_id_url = check_exact_duplicate("JOB-999", "https://example.com/jobs/102", existing_jobs)
    assert dup_id_url == 2

    # Novel job
    no_dup = check_exact_duplicate("JOB-999", "https://example.com/jobs/999", existing_jobs)
    assert no_dup is None


def test_structured_duplicate():
    existing_jobs = [
        {"id": 10, "company": "Google", "title": "Software Engineer", "location": "Bengaluru"},
        {"id": 20, "company": "Microsoft", "title": "Data Scientist", "location": "Hyderabad"},
    ]
    key_map = build_structured_key_map(existing_jobs)

    # Identical structured key
    dup_id = check_structured_duplicate("Google", "Software Engineer", "Bengaluru", key_map)
    assert dup_id == 10

    # Different location
    no_dup = check_structured_duplicate("Google", "Software Engineer", "Pune", key_map)
    assert no_dup is None
