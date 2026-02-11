from datetime import datetime, timedelta
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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
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
    
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, jti


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")
