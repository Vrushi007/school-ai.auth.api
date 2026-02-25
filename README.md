# Authentication Service API

A microservice for managing authentication and authorization for the VYON Boundless Knowledge platform.

## Features

- **User Management**: Create, read, update, and delete users
- **Organization Management**: Manage schools/institutions with hierarchical structure
- **Role-Based Access Control (RBAC)**: Hierarchical roles (system_admin, school_admin, teacher, parent, student)
- **JWT Authentication**: Secure token-based authentication
- **Password Security**: BCrypt password hashing
- **Token Refresh**: Refresh token mechanism for extended sessions
- **Session Management**: Track active sessions and token revocation
- **Password Recovery**: Forgot password and reset password functionality

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
school-ai.auth.api/
├── app/
│   ├── db/
│   │   ├── base.py          # SQLAlchemy declarative base
│   │   ├── session.py       # Database session management
│   │   └── init_db.py       # Database initialization
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── organization.py
│   │   └── session.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── auth.py
│   │   └── token.py
│   ├── routers/             # API route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── roles.py
│   │   └── organizations.py
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
- `organization_id`: Foreign key to Organization
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Role

- `id`: Primary key
- `name`: Role name (system_admin, school_admin, teacher, student, parent)
- `description`: Role description
- `permissions`: JSON field for permissions
- `is_active`: Role status

### Organization

- `id`: Primary key
- `name`: Organization name
- `code`: Unique organization identifier
- `address`: Organization address
- `city`: City
- `state`: State
- `country`: Country (default: India)
- `postal_code`: Postal code
- `phone`: Phone number
- `email`: Contact email
- `website`: Website URL
- `is_active`: Organization status
- `created_at`: Timestamp
- `updated_at`: Timestamp

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
- `PATCH /auth/change-password` - Change password
- `POST /auth/forgot-password` - Request password reset

### Users

- `GET /users` - Get all users (with filters)
- `GET /users/me` - Get current user profile
- `GET /users/{id}` - Get user by ID
- `PATCH /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

### Roles

- `GET /roles` - Get all roles
- `POST /roles` - Create role
- `PUT /roles/{id}` - Update role
- `DELETE /roles/{id}` - Delete role

### Organizations

- `POST /organizations` - Create organization
- `GET /organizations` - Get all organizations (with filters)
- `GET /organizations/{id}` - Get organization by ID
- `PATCH /organizations/{id}` - Update organization
- `DELETE /organizations/{id}` - Delete organization
- `GET /organizations/{id}/users-count` - Get user count for organization

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
