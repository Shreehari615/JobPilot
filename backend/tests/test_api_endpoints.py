"""
Integration tests for FastAPI REST endpoints using TestClient.
"""
from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app

# Ensure tables exist in test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "JobPilot AI" in data["app"]


def test_skills_search_endpoint():
    response = client.get("/api/v1/skills/search?q=python")
    assert response.status_code == 200
    data = response.json()
    assert any(item["name"] == "Python" for item in data)


def test_skills_categories_endpoint():
    response = client.get("/api/v1/skills/categories")
    assert response.status_code == 200
    categories = [c["category"] for c in response.json()]
    assert "languages" in categories
    assert "web" in categories
    assert "ai_ml" in categories


def test_jobs_list_public():
    response = client.get("/api/v1/jobs?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
