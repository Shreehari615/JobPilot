"""Profile management router."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Profile, User, UserPreference
from app.schemas.schemas import PreferencesCreate, PreferencesOut, ProfileCreate, ProfileOut
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("", response_model=ProfileOut)
def update_profile(
    payload: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/preferences", response_model=PreferencesOut)
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    # Deserialize JSON lists
    prefs.preferred_roles = json.loads(prefs.preferred_roles or "[]")
    prefs.preferred_locations = json.loads(prefs.preferred_locations or "[]")
    return prefs


@router.put("/preferences", response_model=PreferencesOut)
def update_preferences(
    payload: PreferencesCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not prefs:
        prefs = UserPreference(user_id=current_user.id)
        db.add(prefs)

    if payload.preferred_roles is not None:
        prefs.preferred_roles = json.dumps(payload.preferred_roles)
    if payload.preferred_locations is not None:
        prefs.preferred_locations = json.dumps(payload.preferred_locations)
    if payload.remote_preference is not None:
        prefs.remote_preference = payload.remote_preference
    if payload.employment_type is not None:
        prefs.employment_type = payload.employment_type
    if payload.min_salary is not None:
        prefs.min_salary = payload.min_salary
    if payload.max_salary is not None:
        prefs.max_salary = payload.max_salary

    db.commit()
    db.refresh(prefs)

    # Deserialize for response
    prefs.preferred_roles = json.loads(prefs.preferred_roles or "[]")
    prefs.preferred_locations = json.loads(prefs.preferred_locations or "[]")
    return prefs
