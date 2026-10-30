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


def test_prevent_false_positive_skill_extraction():
    """Ensure substring matches don't falsely extract skills."""
    prose = """
    MCA student with experience in building scalable applications and secure data storage.
    Engineered a responsive multi-device interface.
    Studied algorithms, data structures, and computer science at S R N M N College.
    Worked on several projects and datasets.
    Taking rest after the exam.
    """
    extracted = extract_skills_from_text(prose)
    # None of these false positives should be extracted from substrings
    assert "Gin" not in extracted, "Gin should not match 'engineered'"
    assert "Go" not in extracted, "Go should not match 'algorithms'"
    assert "R" not in extracted, "R should not match 'S R N M N College'"
    assert "RAG" not in extracted, "RAG should not match 'storage'"
    assert "Scala" not in extracted, "Scala should not match 'scalable'"
    assert "TypeScript" not in extracted, "TypeScript should not match 'projects'"

    # Real skills mentioned in prose should be extracted
    assert "Data Structures" in extracted
    assert "Algorithms" in extracted


def test_extract_special_syntax_skills():
    """Ensure C, C++, C#, CI/CD, REST APIs, YOLO are accurately extracted."""
    text = """
    Technical Skills:
    Programming Languages: Python, Java, C (Basic), C++, C#
    Database: SQL, Oracle, DBMS
    Concepts: Object-Oriented Programming (OOP), SDLC, Agile
    Projects: YOLO object detection, CI/CD integration, REST APIs, Tailwind CSS
    """
    extracted = extract_skills_from_text(text)
    assert "C" in extracted
    assert "C++" in extracted
    assert "C#" in extracted
    assert "CI/CD" in extracted
    assert "REST API" in extracted
    assert "YOLO" in extracted
    assert "DBMS" in extracted
    assert "Object-Oriented Programming" in extracted
    assert "SDLC" in extracted
    assert "Tailwind CSS" in extracted

