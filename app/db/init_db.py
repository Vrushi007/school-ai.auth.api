from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.user import User
from app.utils.security import get_password_hash


def init_db(db: Session) -> None:
    """
    Initialize database with default roles and admin user.
    Hierarchical roles: system_admin > school_admin > teacher > parent > student
    """
    # Create default roles if they don't exist
    default_roles = [
        {
            "name": "system_admin",
            "description": "System Administrator with access to all organizations and full system access",
            "permissions": {
                "organizations": ["create", "read", "update", "delete"],
                "users": ["create", "read", "update", "delete"],
                "roles": ["create", "read", "update", "delete"],
                "content": ["create", "read", "update", "delete"],
                "lessons": ["create", "read", "update", "delete"],
                "questions": ["create", "read", "update", "delete"],
                "reports": ["read"]
            }
        },
        {
            "name": "school_admin",
            "description": "Organization Administrator with full access to their organization's data",
            "permissions": {
                "users": ["create", "read", "update", "delete"],  # Within their organization
                "teachers": ["create", "read", "update", "delete"],
                "students": ["create", "read", "update", "delete"],
                "parents": ["create", "read", "update", "delete"],
                "content": ["create", "read", "update", "delete"],
                "lessons": ["create", "read", "update", "delete"],
                "questions": ["create", "read", "update", "delete"],
                "reports": ["read"]
            }
        },
        {
            "name": "teacher",
            "description": "Teacher with access to lesson planning and student management",
            "permissions": {
                "lessons": ["create", "read", "update", "delete"],
                "questions": ["create", "read", "update", "delete"],
                "students": ["read"],
                "content": ["read"]
            }
        },
        {
            "name": "parent",
            "description": "Parent with access to their children's progress",
            "permissions": {
                "students": ["read"],  # Only their children
                "lessons": ["read"],
                "progress": ["read"],
                "content": ["read"]
            }
        },
        {
            "name": "student",
            "description": "Student with access to learning materials",
            "permissions": {
                "lessons": ["read"],
                "questions": ["read"],
                "answers": ["create", "read"],
                "content": ["read"],
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

    # Create default system admin user if doesn't exist
    admin_email = "admin@vyon.com"
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        system_admin_role = db.query(Role).filter(Role.name == "system_admin").first()
        admin = User(
            email=admin_email,
            username="sysadmin",
            hashed_password=get_password_hash("admin123"),  # Change in production!
            full_name="System Administrator",
            is_active=True,
            is_verified=True,
            role_id=system_admin_role.id,
            organization_id=None  # System admin is not tied to a specific organization
        )
        db.add(admin)
        db.commit()
        print(f"✅ Created default system admin user: {admin_email} / admin123")
