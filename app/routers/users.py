from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.services import user_service
from app.utils.dependencies import get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.get("", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all users (Admin only)."""
    return user_service.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID."""
    # Users can only view their own profile unless they're admin
    if current_user.id != user_id and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return user_service.get_user_by_id(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user."""
    # Users can only update their own profile unless they're admin
    if current_user.id != user_id and current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Only admin can change role_id and is_active
    if current_user.role.name != "admin":
        if user_update.role_id is not None or user_update.is_active is not None:
            raise HTTPException(status_code=403, detail="Only admin can change role or active status")
    
    return user_service.update_user(db, user_id, user_update)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete user (Admin only)."""
    return user_service.delete_user(db, user_id)
