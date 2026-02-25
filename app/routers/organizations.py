from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.schemas.user import UserCreate
from app.services import organization_service, user_service, email_service
from app.utils.dependencies import get_current_user, get_system_admin_user, get_school_admin_or_higher
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    organization: OrganizationCreate,
    current_user: User = Depends(get_system_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new organization. Only system administrators can create organizations.
    Automatically creates an organization admin user for the new organization.
    Sends welcome email to the organization with admin credentials.
    """
    # Create the organization
    new_organization = organization_service.create_organization(db, organization)
    
    # Store credentials for email (before hashing)
    admin_username = f"admin.{new_organization.code.lower()}"
    admin_email = new_organization.email  # Use organization email as admin email
    admin_password = "Welcome@1"
    
    # Create an organization admin user for this organization
    admin_user = UserCreate(
        username=admin_username,
        email=admin_email,
        password=admin_password,
        full_name=f"{new_organization.name} Administrator",
        role_id=2,  # organization admin role
        organization_id=new_organization.id
    )
    
    user_created = False
    try:
        user_service.create_user(db, admin_user)
        user_created = True
    except HTTPException:
        # If user creation fails (e.g., username/email already exists),
        # we don't rollback the organization creation, just log it
        logger.warning(f"Failed to create admin user for organization {new_organization.name}")
    
    # Send welcome email to organization
    if user_created:
        try:
            email_sent = email_service.send_organization_welcome_email(
                organization_name=new_organization.name,
                organization_email=new_organization.email,
                organization_code=new_organization.code,
                admin_username=admin_username,
                admin_password=admin_password,
                admin_email=admin_email
            )
            if email_sent:
                logger.info(f"Welcome email sent to {new_organization.email}")
            else:
                logger.warning(f"Failed to send welcome email to {new_organization.email}")
        except Exception as e:
            # Don't fail the organization creation if email fails
            logger.error(f"Error sending welcome email: {e}")
    
    return new_organization


@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all organizations. System admins see all organizations, organization admins see only their organization.
    """
    # System admin can see all organizations
    if current_user.role.name == "system_admin":
        return organization_service.get_organizations(db, skip, limit, is_active)
    
    # Organization admin and below can only see their organization
    if current_user.organization_id:
        organization = organization_service.get_organization(db, current_user.organization_id)
        return [organization] if organization else []
    
    return []


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get an organization by ID. Users can only access their own organization unless they're system admin.
    """
    organization = organization_service.get_organization(db, organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # System admin can access any organization
    if current_user.role.name == "system_admin":
        return organization
    
    # Other users can only access their own organization
    if current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    return organization


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: int,
    organization_update: OrganizationUpdate,
    current_user: User = Depends(get_school_admin_or_higher),
    db: Session = Depends(get_db)
):
    """
    Update an organization. System admins can update any organization, organization admins can update their own.
    """
    # Check access
    if current_user.role.name != "system_admin" and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this organization"
        )
    
    return organization_service.update_organization(db, organization_id, organization_update)


@router.delete("/{organization_id}", status_code=204)
async def delete_organization(
    organization_id: int,
    current_user: User = Depends(get_system_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete (deactivate) an organization. Only system administrators can delete organizations.
    """
    organization_service.delete_organization(db, organization_id)
    return None


@router.get("/{organization_id}/users-count")
async def get_organization_users_count(
    organization_id: int,
    current_user: User = Depends(get_school_admin_or_higher),
    db: Session = Depends(get_db)
):
    """
    Get count of users in an organization.
    """
    # Check access
    if current_user.role.name != "system_admin" and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization's data"
        )
    
    count = organization_service.get_organization_users_count(db, organization_id)
    return {"organization_id": organization_id, "users_count": count}
