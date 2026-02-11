from sqlalchemy.orm import Session
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate
from fastapi import HTTPException, status


def create_role(db: Session, role: RoleCreate) -> Role:
    """Create a new role."""
    # Check if role already exists
    existing_role = db.query(Role).filter(Role.name == role.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists"
        )
    
    db_role = Role(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_roles(db: Session, skip: int = 0, limit: int = 100):
    """Get all roles."""
    return db.query(Role).offset(skip).limit(limit).all()


def get_role_by_id(db: Session, role_id: int) -> Role:
    """Get role by ID."""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Role:
    """Update role."""
    db_role = get_role_by_id(db, role_id)
    
    update_data = role_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_role, field, value)
    
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int):
    """Delete role."""
    db_role = get_role_by_id(db, role_id)
    
    # Check if role is in use
    if db_role.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete role that is assigned to users"
        )
    
    db.delete(db_role)
    db.commit()
    return {"message": "Role deleted successfully"}
