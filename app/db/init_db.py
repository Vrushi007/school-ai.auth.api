from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.user import User
from app.utils.security import get_password_hash


def init_db(db: Session) -> None:
    """
    Initialize database with default roles and admin user.
    """
    # Create default roles if they don't exist
    default_roles = [
        {
            "name": "admin",
            "description": "Administrator with full system access",
            "permissions": {
                "users": ["create", "read", "update", "delete"],
                "roles": ["create", "read", "update", "delete"],
                "content": ["create", "read", "update", "delete"],
                "lessons": ["create", "read", "update", "delete"],
                "questions": ["create", "read", "update", "delete"]
            }
        },
        {
            "name": "teacher",
            "description": "Teacher with access to lesson planning and student management",
            "permissions": {
                "lessons": ["create", "read", "update", "delete"],
                "questions": ["create", "read", "update", "delete"],
                "students": ["read"]
            }
        },
        {
            "name": "student",
            "description": "Student with access to learning materials",
            "permissions": {
                "lessons": ["read"],
                "questions": ["read"],
                "answers": ["create", "read"]
            }
        },
        {
            "name": "parent",
            "description": "Parent with access to student progress",
            "permissions": {
                "students": ["read"],
                "lessons": ["read"],
                "progress": ["read"]
            }
        }
    ]

    for role_data in default_roles:
        role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not role:
            role = Role(**role_data)
            db.add(role)

    db.commit()

    # Create default admin user if doesn't exist
    admin_email = "admin@vyon.com"
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        admin = User(
            email=admin_email,
            username="admin",
            hashed_password=get_password_hash("admin123"),  # Change in production!
            full_name="System Administrator",
            is_active=True,
            is_verified=True,
            role_id=admin_role.id
        )
        db.add(admin)
        db.commit()
        print(f"✅ Created default admin user: {admin_email} / admin123")
