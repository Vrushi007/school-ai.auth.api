from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from app.schemas.role import RoleResponse
from app.schemas.organization import OrganizationResponse


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str


class UserCreate(UserBase):
    password: str
    role_id: int = 3  # Default to teacher role
    organization_id: int | None = 1  # Default to organization ID 1


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None
    role_id: int | None = None
    organization_id: int | None = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    role_id: int
    organization_id: int | None
    role: RoleResponse
    organization: OrganizationResponse | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
