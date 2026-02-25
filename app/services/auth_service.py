from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.session import Session as UserSession
from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import Token
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    create_password_reset_token,
    verify_password_reset_token
)
from app.services.user_service import create_user, get_user_by_email
from fastapi import HTTPException, status
from app.db.session import settings


def register_user(db: Session, user: UserCreate) -> User:
    """Register a new user."""
    return create_user(db, user)


def register_user_with_tokens(db: Session, user: UserCreate) -> dict:
    """
    Register a new user. 
    User account will be inactive until approved by admin.
    Returns user info instead of tokens since account needs activation.
    """
    # Create the user (will be inactive by default)
    new_user = create_user(db, user)
    
    # Return registration success info without tokens
    # User needs to wait for admin activation
    return {
        "message": "Registration successful! Your account is pending approval by an administrator.",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "full_name": new_user.full_name,
            "is_active": new_user.is_active
        }
    }


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Authenticate user with email and password."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def login(db: Session, user_login: UserLogin) -> Token:
    """Login user and create session."""
    user = authenticate_user(db, user_login.email, user_login.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens (JWT spec: sub must be string)
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.name
    }
    
    access_token, access_jti = create_access_token(token_data)
    refresh_token, refresh_jti = create_refresh_token(token_data)
    
    print(f"🔐 LOGIN: Creating session for user {user.id} with JTI: {access_jti[:30]}...")
    
    # Create session
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    session = UserSession(
        user_id=user.id,
        token_jti=access_jti,
        refresh_token_jti=refresh_jti,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    print(f"✅ SESSION CREATED: ID={session.id}, JTI={session.token_jti[:30]}..., expires={expires_at}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


def refresh_access_token(db: Session, refresh_token: str) -> Token:
    """Refresh access token using refresh token."""
    try:
        payload = decode_token(refresh_token)
        
        # Verify token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        sub = payload.get("sub")
        try:
            user_id = int(sub) if sub is not None else None
        except (TypeError, ValueError):
            user_id = None
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        refresh_jti = payload.get("jti")
        
        # Find session with this refresh token
        session = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.refresh_token_jti == refresh_jti,
            UserSession.is_revoked == False
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token (JWT spec: sub must be string)
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.name
        }
        
        new_access_token, new_access_jti = create_access_token(token_data)
        
        # Update session
        session.token_jti = new_access_jti
        session.expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        db.commit()
        
        return Token(
            access_token=new_access_token,
            refresh_token=refresh_token
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


def logout(db: Session, token_jti: str):
    """Logout user by revoking session."""
    session = db.query(UserSession).filter(UserSession.token_jti == token_jti).first()
    if session:
        session.is_revoked = True
        db.commit()
    return {"message": "Logged out successfully"}


def change_password(db: Session, user: User, old_password: str, new_password: str):
    """Change user password."""
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    user.hashed_password = get_password_hash(new_password)
    
    # Revoke all existing sessions
    db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_revoked == False
    ).update({"is_revoked": True})
    
    db.commit()
    return {"message": "Password changed successfully. Please login again."}


def request_password_reset(db: Session, email: str):
    """
    Request password reset.
    Returns a token that can be used to reset password.
    TODO: Implement SMTP email sending for production use.
    """
    user = get_user_by_email(db, email)
    if not user:
        # For security, don't reveal if email exists
        return {
            "message": "Password reset requested. (Development mode: email not sent)",
            # TODO: Uncomment when SMTP is implemented
            # "message": "If this email is registered, a password reset link has been sent."
        }
    
    if not user.is_active:
        return {
            "message": "Password reset requested. (Development mode: email not sent)",
            # TODO: Uncomment when SMTP is implemented
            # "message": "If this email is registered, a password reset link has been sent."
        }
    
    # Create reset token
    reset_token = create_password_reset_token(user.email)
    
    # TODO: Implement SMTP email sending
    # Example implementation:
    # reset_link = f"{settings.password_reset_url}?token={reset_token}"
    # send_email(
    #     to_email=user.email,
    #     subject="Password Reset Request",
    #     body=f"Click here to reset your password: {reset_link}"
    # )
    
    # For now, we'll return the token (for development/testing only)
    print(f"🔐 Password reset token for {email}: {reset_token}")
    
    # TODO: Store token in database with expiry for additional security
    
    return {
        "message": "Password reset requested. (Development mode: email not sent)",
        "reset_token": reset_token,  # Development only - remove when SMTP is implemented
        # TODO: Uncomment when SMTP is implemented and remove reset_token from response
        # "message": "If this email is registered, a password reset link has been sent."
    }


def reset_password(db: Session, token: str, new_password: str):
    """
    Reset password using a valid reset token.
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    
    # Revoke all existing sessions
    db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_revoked == False
    ).update({"is_revoked": True})
    
    db.commit()
    return {"message": "Password has been reset successfully. Please login with your new password."}
