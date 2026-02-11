from pydantic import BaseModel, ConfigDict
from typing import Dict, Any


class RoleBase(BaseModel):
    name: str
    description: str | None = None
    permissions: Dict[str, Any] = {}


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    permissions: Dict[str, Any] | None = None
    is_active: bool | None = None


class RoleResponse(RoleBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
