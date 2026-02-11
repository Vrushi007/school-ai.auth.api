from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str


class UserCreate(UserBase):
    password: str
    role_id: int = 3  # Default to student role


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None
    role_id: int | None = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    role_id: int
    role: RoleResponse
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str
