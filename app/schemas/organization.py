from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class OrganizationBase(BaseModel):
    name: str
    code: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str = "India"
    postal_code: str | None = None
    phone: str | None = None
    email: EmailStr  # Required field for sending welcome emails
    website: str | None = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    website: str | None = None
    is_active: bool | None = None


class OrganizationResponse(OrganizationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
