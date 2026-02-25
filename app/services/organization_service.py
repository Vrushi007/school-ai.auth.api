from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from typing import List, Optional


def create_organization(db: Session, organization: OrganizationCreate) -> Organization:
    """Create a new organization."""
    # Check if organization code already exists
    existing_organization = db.query(Organization).filter(Organization.code == organization.code).first()
    if existing_organization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization with code '{organization.code}' already exists"
        )
    
    db_organization = Organization(**organization.model_dump())
    db.add(db_organization)
    try:
        db.commit()
        db.refresh(db_organization)
        return db_organization
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating organization. Organization code must be unique."
        )


def get_organization(db: Session, organization_id: int) -> Optional[Organization]:
    """Get an organization by ID."""
    return db.query(Organization).filter(Organization.id == organization_id).first()


def get_organization_by_code(db: Session, code: str) -> Optional[Organization]:
    """Get an organization by code."""
    return db.query(Organization).filter(Organization.code == code).first()


def get_organizations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[Organization]:
    """Get all organizations with pagination."""
    query = db.query(Organization)
    
    if is_active is not None:
        query = query.filter(Organization.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


def update_organization(db: Session, organization_id: int, organization_update: OrganizationUpdate) -> Organization:
    """Update an organization."""
    db_organization = get_organization(db, organization_id)
    if not db_organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Update only provided fields
    update_data = organization_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_organization, field, value)
    
    try:
        db.commit()
        db.refresh(db_organization)
        return db_organization
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating organization"
        )


def delete_organization(db: Session, organization_id: int) -> bool:
    """Delete an organization (soft delete by setting is_active to False)."""
    db_organization = get_organization(db, organization_id)
    if not db_organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Soft delete
    db_organization.is_active = False
    db.commit()
    return True


def get_organization_users_count(db: Session, organization_id: int) -> int:
    """Get count of users in an organization."""
    from app.models.user import User
    return db.query(User).filter(User.organization_id == organization_id).count()
