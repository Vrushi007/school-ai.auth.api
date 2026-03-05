from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash, generate_random_password
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


def create_user(db: Session, user: UserCreate, auto_generate_password: bool = False, created_by_admin: bool = False) -> User:
    """Create a new user. Optionally auto-generate password and activate if created by admin."""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Validate organization_id for non-system_admin users
    from app.models.role import Role
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if role and role.name != "system_admin" and not user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID is required for non-system admin users"
        )
    
    # Generate password if requested
    password = user.password
    if auto_generate_password or not password:
        password = generate_random_password()
    # Always activate if created by admin
    is_active = True if created_by_admin else False
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=get_password_hash(password),
        role_id=user.role_id,
        organization_id=user.organization_id,
        is_active=is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_user.generated_password = password if auto_generate_password or not user.password else None
    # Send account created email if created by admin
    if created_by_admin:
        try:
            from app.services.email_service import email_service
            if db_user.generated_password:
                email_service.send_user_created_email(
                    user_email=db_user.email,
                    user_name=db_user.full_name,
                    username=db_user.username,
                    temporary_password=db_user.generated_password
                )
            else:
                email_service.send_user_activation_email(
                    user_email=db_user.email,
                    user_name=db_user.full_name,
                    username=db_user.username
                )
        except Exception as e:
            logger.error(f"Error sending account created email: {e}")
    return db_user


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100, organization_id: int = None):
    """Get all users, optionally filtered by organization."""
    query = db.query(User)
    
    if organization_id is not None:
        query = query.filter(User.organization_id == organization_id)
    
    return query.offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    """Update user and send activation email if user is being activated."""
    db_user = get_user_by_id(db, user_id)
    
    # Track if user is being activated (was inactive, now active)
    was_inactive = not db_user.is_active
    being_activated = user_update.is_active is True and was_inactive
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    # Send activation email if user was just activated
    if being_activated:
        try:
            from app.services.email_service import email_service
            email_sent = email_service.send_user_activation_email(
                user_email=db_user.email,
                user_name=db_user.full_name,
                username=db_user.username
            )
            if email_sent:
                logger.info(f"Activation email sent to {db_user.email}")
            else:
                logger.warning(f"Failed to send activation email to {db_user.email}")
        except Exception as e:
            # Don't fail the user update if email fails
            logger.error(f"Error sending activation email: {e}")
    
    return db_user


def delete_user(db: Session, user_id: int):
    """Delete user."""
    db_user = get_user_by_id(db, user_id)
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
