"""Authentication router – register (with OTP), login, me, forgot/reset password."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import EmailOTP, Profile, User, UserPreference
from app.schemas.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    SendOTPRequest,
    TokenResponse,
    UserOut,
    VerifyOTPRequest,
)
from app.utils.dependencies import get_current_user
from app.utils.email_utils import (
    generate_otp,
    generate_reset_token,
    send_otp_email,
    send_password_reset_email,
)
from app.utils.logger import get_logger
from app.utils.security import create_access_token, hash_password, verify_password

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


# ── Send OTP ─────────────────────────────────────────────────────────────────

@router.post("/send-otp", response_model=MessageResponse)
def send_otp(
    payload: SendOTPRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Generate a 6-digit OTP and email it to the given address."""
    email = payload.email.lower().strip()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=400,
            detail="This email is already registered. Please log in instead.",
        )

    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

    db.add(EmailOTP(email=email, otp=otp, expires_at=expires_at))
    db.commit()

    background_tasks.add_task(send_otp_email, email, otp, settings.OTP_EXPIRY_MINUTES)
    logger.info(f"OTP sent to {email}")
    return MessageResponse(message=f"Verification code sent to {email}.")


# ── Verify OTP ───────────────────────────────────────────────────────────────

@router.post("/verify-otp", response_model=MessageResponse)
def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Check that the OTP is valid (without marking it used – registration does that)."""
    email = payload.email.lower().strip()
    now = datetime.now(timezone.utc)

    record = (
        db.query(EmailOTP)
        .filter(
            EmailOTP.email == email,
            EmailOTP.otp == payload.otp,
            EmailOTP.is_used == False,  # noqa: E712
            EmailOTP.expires_at > now,
        )
        .order_by(EmailOTP.created_at.desc())
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code. Please request a new one.",
        )

    return MessageResponse(message="OTP verified successfully.")


# ── Register (requires valid OTP) ────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Requires a valid, unused OTP that was sent to payload.email.
    """
    email = payload.email.lower().strip()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Re-validate OTP at registration time
    now = datetime.now(timezone.utc)
    otp_record = (
        db.query(EmailOTP)
        .filter(
            EmailOTP.email == email,
            EmailOTP.is_used == False,  # noqa: E712
            EmailOTP.expires_at > now,
        )
        .order_by(EmailOTP.created_at.desc())
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="Email not verified. Please verify your email with an OTP before registering.",
        )

    # Create user
    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        is_email_verified=True,
    )
    db.add(user)
    db.flush()

    # Mark OTP as used
    otp_record.is_used = True

    # Empty profile and preferences
    profile = Profile(user_id=user.id, full_name=payload.full_name)
    prefs = UserPreference(user_id=user.id)
    db.add(profile)
    db.add(prefs)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email})
    logger.info(f"New user registered (email verified): {user.email}")
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=payload.full_name,
        is_admin=user.is_admin,
    )


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email, User.is_active == True).first()  # noqa: E712
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


# ── Me ────────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ── Forgot Password ───────────────────────────────────────────────────────────

@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Send a password-reset link email if the address is registered."""
    email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()

    # Always return success to prevent user enumeration
    if not user:
        return MessageResponse(
            message="If that email is registered, a reset link has been sent."
        )

    token = generate_reset_token()
    user.password_reset_token = token
    user.password_reset_expires = datetime.now(timezone.utc) + timedelta(
        hours=settings.RESET_TOKEN_EXPIRY_HOURS
    )
    db.commit()

    # Frontend must handle the /reset-password?token=... route
    reset_url = f"http://localhost:5173/reset-password?token={token}"
    background_tasks.add_task(
        send_password_reset_email, email, reset_url, settings.RESET_TOKEN_EXPIRY_HOURS
    )
    logger.info(f"Password reset link sent to {email}")
    return MessageResponse(
        message="If that email is registered, a reset link has been sent."
    )


# ── Reset Password ────────────────────────────────────────────────────────────

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Consume the reset token and set a new password."""
    now = datetime.now(timezone.utc)
    user = (
        db.query(User)
        .filter(
            User.password_reset_token == payload.token,
            User.password_reset_expires > now,
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset link. Please request a new one.",
        )

    user.hashed_password = hash_password(payload.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.commit()

    logger.info(f"Password reset successful for {user.email}")
    return MessageResponse(message="Password reset successful. You can now log in.")

