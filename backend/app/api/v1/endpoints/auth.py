from datetime import timedelta
from typing import Any
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash
from app.crud.crud_user import user as crud_user
from app.models.user import User
from app.schemas.token import Token, LoginRequest
from app.schemas.user import UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
def login_json(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
) -> Any:
    """Authenticate user with JSON credentials and return JWT access token."""
    user = crud_user.authenticate(
        db, email=login_data.email, password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password.",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user,
    }


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """OAuth2 compatible token login, for Swagger UI authentication dialog."""
    user = crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password.",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user,
    }


class AdminSetupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)
    setup_token: str = Field(min_length=16, max_length=256)


@router.post("/setup-admin")
def setup_admin_password(
    setup_data: AdminSetupRequest,
    db: Session = Depends(get_db),
) -> dict:
    """One-time administrator password setup using a server-side setup token."""
    configured_token = settings.ADMIN_SETUP_TOKEN
    if not configured_token or not secrets.compare_digest(setup_data.setup_token, configured_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid administrator setup token.")

    admin = db.query(User).filter(User.email == setup_data.email).first()
    if not admin or not admin.is_active or not admin.is_superuser:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrator account not found.")
    if getattr(admin, "password_initialized_at", None) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Administrator password has already been initialized.")

    admin.hashed_password = get_password_hash(setup_data.password)
    from sqlalchemy import func
    admin.password_initialized_at = db.query(func.now()).scalar()
    db.add(admin)
    db.commit()
    return {"status": "success", "message": "Administrator password initialized. You can now sign in normally."}


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get the currently logged in user profile and assigned role."""
    return current_user
