"""
backend/auth/models.py

SQLAlchemy ORM model for the `users` table.
Uses the shared PostgreSQL engine from backend/Database/db.py.
No existing tables are modified.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase
from backend.Database.db import engine

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class User(Base):
    """Represents a registered OmniBrain user."""

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(50), unique=True, nullable=False, index=True)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    password_hash: str = Column(Text, nullable=False)
    created_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


def create_users_table() -> None:
    """
    Create the `users` table in PostgreSQL if it does not already exist.
    Called once at application startup — safe to call repeatedly.
    """
    if engine is None:
        logger.warning("Database engine is not configured; skipping users table creation.")
        return

    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except SQLAlchemyError as exc:
        logger.warning("Skipping users table creation because PostgreSQL is unavailable: %s", exc)
