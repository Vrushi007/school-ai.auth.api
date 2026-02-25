from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.db.session import settings
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> tuple[str, str]:
    """
    Create a JWT access token.
    Returns: (token, jti)
    """
    to_encode = data.copy()
    jti = secrets.token_urlsafe(32)
    to_encode.update({"jti": jti})
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, jti


def create_refresh_token(data: Dict[str, Any]) -> tuple[str, str]:
    """
    Create a JWT refresh token.
    Returns: (token, jti)
    """
    to_encode = data.copy()
    jti = secrets.token_urlsafe(32)
    to_encode.update({"jti": jti})
    
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, jti


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT token."""
    try:
        print(f"🔐 Attempting to decode token: {token[:50]}...")  # DEBUG
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ Token decoded successfully: {payload}")  # DEBUG
        return payload
    except JWTError as e:
        print(f"❌ JWTError during decode: {e}")  # DEBUG
        raise ValueError(f"Invalid token: {e}")
    except Exception as e:
        print(f"❌ Unexpected error during decode: {type(e).__name__}: {e}")  # DEBUG
        raise ValueError("Invalid token")


def create_password_reset_token(email: str) -> str:
    """
    Create a password reset token.
    Returns: token (expires in 1 hour)
    """
    to_encode = {"email": email, "type": "password_reset"}
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    """
    Verify password reset token and return email if valid.
    Returns: email or None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        email: str = payload.get("email")
        return email
    except JWTError:
        return None
