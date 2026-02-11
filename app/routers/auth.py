from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, ChangePassword
from app.schemas.token import Token, RefreshTokenRequest
from app.services import auth_service
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=dict, status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    new_user = auth_service.register_user(db, user)
    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "email": new_user.email
    }


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    return auth_service.login(db, user_login)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    return auth_service.refresh_access_token(db, refresh_request.refresh_token)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout and revoke current session."""
    # Get token JTI from current user's context
    # This would need to be passed through the dependency
    return auth_service.logout(db, "")  # Implementation needs token_jti


@router.patch("/change-password")
async def change_password(
    password_change: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password."""
    return auth_service.change_password(
        db,
        current_user,
        password_change.old_password,
        password_change.new_password
    )
