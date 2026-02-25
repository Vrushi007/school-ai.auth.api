from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.session import Session as UserSession
from app.utils.security import decode_token
from datetime import datetime, timezone

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        print(f"🔍 Token payload: {payload}")  # DEBUG
        
        # Verify token type
        if payload.get("type") != "access":
            print(f"❌ Invalid token type: {payload.get('type')}")  # DEBUG
            raise credentials_exception
        
        # JWT sub is string (per spec); convert to int for user_id (handle legacy int sub)
        sub = payload.get("sub")
        try:
            user_id = int(sub) if sub is not None else None
        except (TypeError, ValueError):
            user_id = None
        jti: str = payload.get("jti")
        
        print(f"🔍 Extracted - user_id: {user_id}, jti: {jti[:20] if jti else None}...")  # DEBUG
        
        if user_id is None or jti is None:
            print(f"❌ Missing user_id or jti in token")  # DEBUG
            raise credentials_exception
            
    except ValueError as e:
        print(f"❌ Token decode error: {e}")  # DEBUG
        raise credentials_exception
    
    # Check if session is valid and not revoked
    session = db.query(UserSession).filter(
        UserSession.token_jti == jti,
        UserSession.is_revoked == False
    ).first()
    
    print(f"🔍 Session lookup for jti {jti[:20]}... -> Found: {session is not None}")  # DEBUG
    
    if not session:
        print(f"❌ No valid session found for jti")  # DEBUG
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked or expired"
        )
    
    # Check if session is expired (use UTC-aware now; DB stores timezone-aware)
    if session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Get current user and verify admin role (backward compatibility)."""
    if current_user.role.name not in ["system_admin", "school_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_system_admin_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Get current user and verify system admin role."""
    if current_user.role.name != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can perform this action"
        )
    return current_user


async def get_school_admin_or_higher(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Get current user and verify school admin or system admin role."""
    if current_user.role.name not in ["system_admin", "school_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires school administrator or higher privileges"
        )
    return current_user


def verify_school_access(current_user: User, target_school_id: int) -> bool:
    """
    Verify if user has access to a specific organization.
    System admins have access to all organizations.
    Other users only have access to their own organization.
    """
    if current_user.role.name == "system_admin":
        return True
    
    return current_user.organization_id == target_school_id


def require_school_access(current_user: User, target_school_id: int) -> None:
    """
    Require user to have access to a specific organization, raise exception if not.
    """
    if not verify_school_access(current_user, target_school_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization's data"
        )
