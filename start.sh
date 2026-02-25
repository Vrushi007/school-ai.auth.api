#!/bin/bash

echo "Starting Authentication Service..."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Initialize database with default data
echo "Initializing database with default roles and admin user..."
python -c "
from app.db.session import SessionLocal
from app.db.init_db import init_db

db = SessionLocal()
try:
    init_db(db)
finally:
    db.close()
"

# Start the FastAPI application
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
