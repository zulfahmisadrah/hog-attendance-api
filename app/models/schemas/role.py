from typing import Optional

from fastapi_permissions import Allow, Authenticated
from pydantic import BaseModel


class RoleBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None

    def __acl__(self):
        return [
            (Allow, Authenticated, "role_read"),
            (Allow, "role:superadmin", ("role_create", "role_update", "role_delete")),
        ]


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class Role(RoleBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True
