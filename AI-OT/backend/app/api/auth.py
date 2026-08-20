"""Login endpoint for local prototype users."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, verify_password
from app.database.session import get_db
from app.models.entities import AuditLog, User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["authentication"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: DbSession) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == credentials.email))
    if user is None or not user.is_active or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db.add(AuditLog(user=user, action="login", entity_type="user", entity_id=user.id, details={"prototype": True}))
    db.commit()
    return TokenResponse(access_token=create_access_token(user.id), user=UserResponse(id=user.id, email=user.email, display_name=user.display_name, role=user.role))


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse(id=current_user.id, email=current_user.email, display_name=current_user.display_name, role=current_user.role)
