"""
Database engine, session factory, and declarative base.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine_kwargs = {"pool_pre_ping": True, "echo": settings.DEBUG, "connect_args": connect_args}
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({"pool_size": 10, "max_overflow": 20})

engine = create_engine(
    settings.DATABASE_URL,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency – yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
