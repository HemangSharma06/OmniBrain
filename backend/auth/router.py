"""
backend/auth/router.py

FastAPI router exposing three additive auth endpoints:
  POST /auth/register  — create account
  POST /auth/login     — authenticate, receive JWT
  GET  /auth/me        — return current user info (protected)

These endpoints do NOT modify any existing route.
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    get_db_session,
    hash_password,
    verify_password,
)
from backend.auth.models import User
from backend.auth.schemas import Token, UserCreate, UserLogin, UserOut

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])


# ── POST /auth/register ────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(user_data: UserCreate, db: Session = Depends(get_db_session)) -> UserOut:
    """
    Create a new user.

    - Username must be unique (3–50 alphanumeric / underscore / hyphen characters).
    - Email must be unique and valid.
    - Password is hashed with bcrypt before storage.
    """
    # Check uniqueness of username
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user_data.username}' is already taken.",
        )

    # Check uniqueness of email
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info("New user registered: %s (%s)", new_user.username, new_user.email)
    return UserOut.model_validate(new_user)


# ── POST /auth/login ───────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and receive a JWT access token",
)
def login(credentials: UserLogin, db: Session = Depends(get_db_session)) -> Token:
    """
    Verify credentials and return a signed JWT.

    The token encodes the username in the `sub` claim and expires after
    JWT_EXPIRE_MINUTES (default 1440 = 24 hours).
    """
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    logger.info("User logged in: %s", user.username)
    return Token(access_token=access_token, token_type="bearer")


# ── GET /auth/me ───────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserOut,
    summary="Return the currently authenticated user",
)
def get_me(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    """Return the profile of the user identified by the supplied JWT."""
    return current_user
