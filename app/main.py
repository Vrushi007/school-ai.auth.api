from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routers import auth, users, roles, organizations
from app.db.session import SessionLocal
from app.db.init_db import init_db

# Get environment
environment = os.getenv("ENVIRONMENT", "development")

app = FastAPI(
    title="Authentication Service API",
    description="Microservice for managing authentication and authorization for VYON platform",
    version="1.0.0"
)

# CORS configuration - restrict origins in production
if environment == "production":
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        ""
    ).split(",") if os.getenv("ALLOWED_ORIGINS") else []
    # Remove empty strings
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
else:
    # Development: allow all origins
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    """Initialize database with default roles on startup"""
    db = SessionLocal()
    try:
        init_db(db)
        print("✅ Database initialized with default roles")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    finally:
        db.close()

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(organizations.router)


@app.get("/")
def root():
    return {
        "message": "Authentication Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
