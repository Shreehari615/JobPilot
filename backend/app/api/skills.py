"""
Skills router – taxonomy discovery, autocomplete, category lookup, and related skills.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.ai.skill_taxonomy import (
    ALL_CATEGORIES,
    ALL_SKILLS,
    SKILL_TAXONOMY,
    get_related_skills,
    get_skill_category,
    normalize_skill,
)

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("/search")
def search_skills(
    q: str = Query("", description="Skill search prefix/query"),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Search known skills by query for autocomplete.
    """
    q_clean = q.strip().lower()
    if not q_clean:
        return ALL_SKILLS[:limit]

    matches = [
        {"name": s, "category": SKILL_TAXONOMY.get(s)}
        for s in ALL_SKILLS
        if q_clean in s.lower()
    ]
    return matches[:limit]


@router.get("/categories")
def get_categories():
    """
    Return all available skill categories and count of skills per category.
    """
    cat_counts: Dict[str, int] = {}
    for cat in ALL_CATEGORIES:
        cat_counts[cat] = sum(1 for c in SKILL_TAXONOMY.values() if c == cat)
    return [{"category": cat, "count": count} for cat, count in cat_counts.items()]


@router.get("/category/{category_name}")
def get_skills_by_category(category_name: str):
    """
    List all skills under a given category.
    """
    skills = [
        skill for skill, cat in SKILL_TAXONOMY.items()
        if cat.lower() == category_name.lower()
    ]
    if not skills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_name}' not found",
        )
    return {"category": category_name, "skills": sorted(skills)}


@router.get("/related/{skill_name}")
def get_related(skill_name: str):
    """
    Find related or prerequisite skills for a given skill.
    """
    canonical = normalize_skill(skill_name) or skill_name
    related = get_related_skills(canonical)
    return {
        "skill": canonical,
        "category": get_skill_category(canonical),
        "related": related,
    }
