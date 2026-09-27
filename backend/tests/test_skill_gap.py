"""
Unit tests for Skill Gap Engine.
"""
from app.services.skill_gap import analyze_skill_gap


def test_analyze_skill_gap():
    candidate_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "JavaScript"]
    job_skills = ["Python", "FastAPI", "React", "AWS", "Docker"]

    res = analyze_skill_gap(candidate_skills, job_skills)
    assert "Python" in res.matching
    assert "FastAPI" in res.matching
    assert "Docker" in res.matching

    # JavaScript is related to React (partial)
    assert "React" in res.partial or "React" in res.missing

    # AWS is missing
    assert "AWS" in res.missing

    assert 0.0 <= res.match_rate <= 100.0
    assert len(res.matching) > 0
