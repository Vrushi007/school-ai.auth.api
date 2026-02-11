from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.services import role_service
from app.utils.dependencies import get_current_admin_user, get_current_user
from app.models.user import User

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=List[RoleResponse])
async def get_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all roles."""
    return role_service.get_roles(db, skip=skip, limit=limit)


@router.post("", response_model=RoleResponse, status_code=201)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new role (Admin only)."""
    return role_service.create_role(db, role)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update role (Admin only)."""
    return role_service.update_role(db, role_id, role_update)


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete role (Admin only)."""
    return role_service.delete_role(db, role_id)
