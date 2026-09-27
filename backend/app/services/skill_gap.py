"""
Skill Gap Engine – classifies job's required skills vs candidate skills
into: matching / partial / missing

Used for recommendation explanations and the Skill Gaps dashboard page.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

from app.ai.skill_taxonomy import get_related_skills
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SkillGapResult:
    matching: List[str]    # Candidate has the skill
    partial: List[str]     # Candidate has a related skill
    missing: List[str]     # Candidate lacks the skill completely
    match_rate: float      # Percentage of required skills matched (full or partial)


def analyze_skill_gap(
    candidate_skills: List[str],
    required_skills: List[str],
) -> SkillGapResult:
    """
    Compare candidate's skills against a job's required skills.

    matching: candidate has exact skill
    partial:  candidate has a skill in the RELATED_SKILLS graph
    missing:  candidate has neither
    """
    candidate_set: Set[str] = {s.lower() for s in candidate_skills}
    matching: List[str] = []
    partial: List[str] = []
    missing: List[str] = []

    for skill in required_skills:
        if not skill:
            continue
        skill_lower = skill.lower()

        if skill_lower in candidate_set or skill in candidate_skills:
            matching.append(skill)
        else:
            # Check related skills
            related = get_related_skills(skill)
            found_partial = False
            for rel in related:
                if rel.lower() in candidate_set:
                    partial.append(skill)
                    found_partial = True
                    break
            if not found_partial:
                missing.append(skill)

    total = len(required_skills)
    if total == 0:
        match_rate = 1.0
    else:
        match_rate = (len(matching) + 0.5 * len(partial)) / total

    return SkillGapResult(
        matching=matching,
        partial=partial,
        missing=missing,
        match_rate=round(match_rate * 100, 1),
    )


def get_top_skill_gaps(
    user_recommendations: List[Dict],
    top_n: int = 5,
) -> List[Dict]:
    """
    Aggregate missing skills across top recommendations
    to identify the most impactful skills to learn.

    user_recommendations: list of recommendation dicts with 'explanation' field
    """
    gap_counts: Dict[str, int] = {}
    for rec in user_recommendations:
        explanation = rec.get("explanation") or {}
        if isinstance(explanation, str):
            import json
            try:
                explanation = json.loads(explanation)
            except Exception:
                explanation = {}
        missing = explanation.get("missing_skills", [])
        for skill in missing:
            gap_counts[skill] = gap_counts.get(skill, 0) + 1

    sorted_gaps = sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"skill": skill, "count": count} for skill, count in sorted_gaps[:top_n]]
