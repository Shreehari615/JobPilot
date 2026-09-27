"""
JWT token creation and verification utilities.
Passwords are hashed using bcrypt via passlib.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from app.config import get_settings

settings = get_settings()

try:
    from jose import JWTError, jwt
except ImportError:
    import jwt
    from jwt.exceptions import PyJWTError as JWTError

try:
    import bcrypt

    def hash_password(plain: str) -> str:
        # bcrypt limit is 72 bytes
        pwd_bytes = plain.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

    def verify_password(plain: str, hashed: str) -> bool:
        pwd_bytes = plain.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))
except ImportError:
    import hashlib

    def hash_password(plain: str) -> str:
        return hashlib.sha256(plain.encode()).hexdigest()

    def verify_password(plain: str, hashed: str) -> bool:
        return hashlib.sha256(plain.encode()).hexdigest() == hashed


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
