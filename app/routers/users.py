from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.services import user_service
from app.utils.dependencies import (
    get_current_user, 
    get_current_admin_user, 
    get_school_admin_or_higher,
    require_school_access
)
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.get("", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    organization_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_school_admin_or_higher)
):
    """
    Get all users. 
    - System admins can see all users across all organizations
    - Organization admins can only see users from their organization
    """
    # System admin can see all users or filter by organization
    if current_user.role.name == "system_admin":
        return user_service.get_users(db, skip=skip, limit=limit, organization_id=organization_id)
    
    # Organization admin can only see users from their own organization
    if current_user.role.name == "school_admin":
        if organization_id and organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only view users from your own organization"
            )
        return user_service.get_users(db, skip=skip, limit=limit, organization_id=current_user.organization_id)
    
    raise HTTPException(status_code=403, detail="Not authorized")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID."""
    target_user = user_service.get_user_by_id(db, user_id)
    
    # Users can view their own profile
    if current_user.id == user_id:
        return target_user
    
    # System admin can view any user
    if current_user.role.name == "system_admin":
        return target_user
    
    # Organization admin can view users from their organization
    if current_user.role.name == "school_admin":
        if target_user.organization_id == current_user.organization_id:
            return target_user
    
    raise HTTPException(status_code=403, detail="Not authorized to view this user")


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user."""
    target_user = user_service.get_user_by_id(db, user_id)
    
    # Check permissions
    is_self_update = current_user.id == user_id
    is_system_admin = current_user.role.name == "system_admin"
    is_school_admin = current_user.role.name == "school_admin" and target_user.organization_id == current_user.organization_id
    
    if not (is_self_update or is_system_admin or is_school_admin):
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    # Only admins can change role_id, is_active, and organization_id
    if not (is_system_admin or is_school_admin):
        if any([
            user_update.role_id is not None,
            user_update.is_active is not None,
            user_update.organization_id is not None
        ]):
            raise HTTPException(
                status_code=403, 
                detail="Only administrators can change role, active status, or organization"
            )
    
    # Organization admin cannot change organization_id to a different organization
    if is_school_admin and not is_system_admin:
        if user_update.organization_id and user_update.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403,
                detail="Organization administrators cannot transfer users to other organizations"
            )
    
    return user_service.update_user(db, user_id, user_update)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_school_admin_or_higher)
):
    """Delete user. System admin can delete any user, organization admin can delete users from their organization."""
    target_user = user_service.get_user_by_id(db, user_id)
    
    # System admin can delete any user
    if current_user.role.name == "system_admin":
        return user_service.delete_user(db, user_id)
    
    # Organization admin can only delete users from their organization
    if current_user.role.name == "school_admin":
        if target_user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403,
                detail="You can only delete users from your own organization"
            )
        return user_service.delete_user(db, user_id)
    
    raise HTTPException(status_code=403, detail="Not authorized")
