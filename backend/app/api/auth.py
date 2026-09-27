"""Authentication router – register, login, me."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Profile, User, UserPreference
from app.schemas.schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.utils.dependencies import get_current_user
from app.utils.logger import get_logger
from app.utils.security import create_access_token, hash_password, verify_password

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.flush()

    # Create empty profile and preferences
    profile = Profile(user_id=user.id, full_name=payload.full_name)
    prefs = UserPreference(user_id=user.id)
    db.add(profile)
    db.add(prefs)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email})
    logger.info(f"New user registered: {user.email}")
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=payload.full_name,
        is_admin=user.is_admin,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email, User.is_active == True).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    logger.info(f"User logged in: {user.email}")

    full_name = user.profile.full_name if user.profile else None
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=full_name,
        is_admin=user.is_admin,
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
