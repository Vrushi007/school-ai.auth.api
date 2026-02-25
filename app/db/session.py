from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:password@localhost:5432/secure_identity_vault"
    )
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
    
    # Email Configuration
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "noreply@vyon.com")
    smtp_from_name: str = os.getenv("SMTP_FROM_NAME", "VYON Boundless Knowledge")
    
    # Frontend URLs
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    email_verification_url: str = os.getenv("EMAIL_VERIFICATION_URL", "http://localhost:3000/verify-email")
    password_reset_url: str = os.getenv("PASSWORD_RESET_URL", "http://localhost:3000/reset-password")

    class Config:
        env_file = ".env"


settings = Settings()
DATABASE_URL = settings.database_url

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency for getting database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
