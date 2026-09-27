"""
Unit tests for the 5-factor weighted Matching Engine.
"""
from app.services.matching_engine import (
    compute_education_score,
    compute_experience_score,
    compute_match,
    compute_preference_score,
    compute_skill_score,
)


def test_compute_skill_score():
    candidate_skills = ["Python", "React", "PostgreSQL", "Docker"]
    required_skills = ["Python", "PostgreSQL", "AWS"]

    score = compute_skill_score(candidate_skills, required_skills)
    assert 60.0 <= score <= 70.0  # 2 of 3 matched = ~66.7%


def test_compute_experience_score():
    # Exactly meets range
    score_met = compute_experience_score(3.0, 2.0, 5.0)
    assert score_met == 100.0

    # Under requirement
    score_under = compute_experience_score(1.0, 3.0, 5.0)
    assert score_under < 100.0
    assert score_under > 0.0

    # Fresher looking at 0-exp role
    score_fresh = compute_experience_score(0.0, 0.0, 1.0)
    assert score_fresh == 100.0


def test_compute_education_score():
    score = compute_education_score("B.Tech", 5, "B.Tech / MCA or equivalent")
    assert score == 100.0


def test_compute_preference_score():
    prefs = {
        "preferred_roles": ["Software Engineer", "Full Stack Developer"],
        "preferred_locations": ["Bengaluru", "Remote"],
        "remote_preference": "hybrid",
        "employment_type": "full-time",
    }
    job = {
        "title": "Senior Software Engineer",
        "location": "Bengaluru",
        "work_mode": "hybrid",
        "job_type": "full-time",
    }
    score = compute_preference_score(prefs, job)
    assert score >= 80.0


def test_compute_match_combined():
    candidate = {
        "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
        "education": [{"degree": "B.Tech in Computer Science"}],
        "total_experience_years": 3.0,
        "preferences": {
            "preferred_roles": ["Backend Developer", "Full Stack Developer"],
            "preferred_locations": ["Bengaluru"],
            "remote_preference": "hybrid",
            "employment_type": "full-time",
        },
        "embedding": None,
    }

    job = {
        "title": "Python Backend Developer",
        "description": "Looking for a Python and FastAPI developer with PostgreSQL experience.",
        "skills": [
            {"skill_name": "Python", "is_required": True},
            {"skill_name": "FastAPI", "is_required": True},
            {"skill_name": "PostgreSQL", "is_required": True},
            {"skill_name": "Docker", "is_required": False},
        ],
        "experience_min": 2.0,
        "experience_max": 5.0,
        "education_required": "B.Tech / MCA",
        "location": "Bengaluru",
        "work_mode": "hybrid",
        "job_type": "full-time",
        "embedding": None,
    }

    match_result = compute_match(candidate, job)
    assert match_result.overall_score >= 80.0
    assert match_result.skill_score == 100.0
    assert match_result.experience_score == 100.0
    assert "matched_skills" in match_result.explanation
    assert len(match_result.explanation["matched_skills"]) >= 3
