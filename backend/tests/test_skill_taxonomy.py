"""
Unit tests for Skill Taxonomy & extraction.
"""
from app.ai.skill_taxonomy import (
    extract_skills_from_text,
    get_related_skills,
    get_skill_category,
    is_recognized_skill,
    normalize_skill,
)


def test_normalize_skill():
    assert normalize_skill("python") == "Python"
    assert normalize_skill("py") == "Python"
    assert normalize_skill("react.js") == "React"
    assert normalize_skill("reactjs") == "React"
    assert normalize_skill("aws") == "AWS"
    assert normalize_skill("amazon web services") == "AWS"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("unknownskill12345") is None


def test_skill_categories():
    assert get_skill_category("Python") == "languages"
    assert get_skill_category("React") == "web"
    assert get_skill_category("FastAPI") == "web"
    assert get_skill_category("Machine Learning") == "ai_ml"
    assert get_skill_category("Docker") == "cloud"
    assert get_skill_category("PostgreSQL") == "databases"


def test_extract_skills_from_text():
    sample_text = """
    We are looking for a Senior Full Stack Engineer with strong experience in Python,
    FastAPI, and React.js. Knowledge of PostgreSQL, Redis, and Docker in AWS is essential.
    Experience with Machine Learning or PyTorch is a plus.
    """
    extracted = extract_skills_from_text(sample_text)
    assert "Python" in extracted
    assert "FastAPI" in extracted
    assert "React" in extracted
    assert "PostgreSQL" in extracted
    assert "Redis" in extracted
    assert "Docker" in extracted
    assert "AWS" in extracted


def test_related_skills():
    related = get_related_skills("React")
    assert any("Vue.js" in r or "Angular" in r or "Svelte" in r for r in related)
