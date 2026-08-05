"""
backend/auth/schemas.py

Pydantic v2 schemas for auth request/response bodies.
These are additive — no existing schemas are changed.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ── Registration ───────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Payload for POST /auth/register."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="3–50 alphanumeric characters, underscores, or hyphens.",
    )
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters.")


# ── Login ──────────────────────────────────────────────────────────────────────

class UserLogin(BaseModel):
    """Payload for POST /auth/login."""

    username: str
    password: str


# ── Token responses ────────────────────────────────────────────────────────────

class Token(BaseModel):
    """Returned by /auth/login."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded payload stored inside a JWT."""

    username: str | None = None


# ── User info ──────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    """Safe user data returned to the client (no password hash)."""

    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
