# Authentication Service API

A microservice for managing authentication and authorization for the VYON Boundless Knowledge platform.

## Features

- **User Management**: Create, read, update, and delete users
- **Role-Based Access Control (RBAC)**: Assign roles and permissions to users
- **JWT Authentication**: Secure token-based authentication
- **Password Security**: BCrypt password hashing
- **Token Refresh**: Refresh token mechanism for extended sessions
- **User Roles**: Support for Teacher, Student, Admin, and Parent roles
- **Session Management**: Track active sessions and token revocation

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy 2.x**: ORM for database operations
- **Alembic**: Database migrations
- **PostgreSQL**: Relational database
- **Pydantic v2**: Data validation
- **PyJWT**: JSON Web Token implementation
- **Passlib**: Password hashing with bcrypt
- **Docker & Docker Compose**: Containerization

## Project Structure

```
auth-service/
├── app/
│   ├── db/
│   │   ├── base.py          # SQLAlchemy declarative base
│   │   ├── session.py       # Database session management
│   │   └── init_db.py       # Database initialization
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── role.py
│   │   └── session.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── auth.py
│   │   └── token.py
│   ├── routers/             # API route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── roles.py
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   └── role_service.py
│   ├── utils/               # Utility functions
│   │   ├── security.py      # Password hashing, JWT
│   │   └── dependencies.py  # FastAPI dependencies
│   └── main.py              # FastAPI application
├── alembic/                 # Database migrations
│   ├── versions/
│   └── env.py
├── alembic.ini              # Alembic configuration
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Database Models

### User

- `id`: Primary key
- `email`: Unique email address
- `username`: Unique username
- `hashed_password`: BCrypt hashed password
- `full_name`: User's full name
- `is_active`: Account status
- `is_verified`: Email verification status
- `role_id`: Foreign key to Role
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Role

- `id`: Primary key
- `name`: Role name (Teacher, Student, Admin, Parent)
- `description`: Role description
- `permissions`: JSON field for permissions

### Session

- `id`: Primary key
- `user_id`: Foreign key to User
- `token_jti`: JWT token ID
- `refresh_token_jti`: Refresh token ID
- `expires_at`: Token expiration
- `created_at`: Session creation time
- `is_revoked`: Revocation status

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout and revoke tokens
- `POST /auth/verify-email` - Verify email address
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

### Users

- `GET /users` - Get all users (Admin only)
- `GET /users/{id}` - Get user by ID
- `GET /users/me` - Get current user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user (Admin only)
- `PATCH /users/{id}/change-password` - Change password

### Roles

- `GET /roles` - Get all roles
- `POST /roles` - Create role (Admin only)
- `PUT /roles/{id}` - Update role (Admin only)
- `DELETE /roles/{id}` - Delete role (Admin only)

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- Docker (optional)

### Installation

#### Using Docker (Recommended)

```bash
# Build the Docker image
docker build -t auth-service .

# Run with Docker
docker run -p 8080:8080 \
  -e DATABASE_URL=postgresql://user:password@localhost:5432/auth_db \
  -e SECRET_KEY=your-secret-key \
  -e ENVIRONMENT=development \
  auth-service
```

#### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/auth_db

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Email (for verification)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## API Documentation

After starting the server, visit:

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Security Features

- **Password Hashing**: Uses bcrypt with automatic salt generation
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Token Refresh**: Separate refresh tokens for extended sessions
- **Token Revocation**: Session-based token blacklisting
- **Role-Based Access**: Fine-grained permission control
- **CORS Protection**: Configurable allowed origins
- **SQL Injection Protection**: SQLAlchemy ORM parameterized queries

## Development

```bash
# Run tests (when implemented)
pytest

# Format code
black app/

# Lint code
ruff check app/
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for AWS, Google Cloud, and Azure.

## License

Proprietary - VYON Boundless Knowledge © 2026
