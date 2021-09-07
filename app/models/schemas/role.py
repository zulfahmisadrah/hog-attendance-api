from typing import Optional

from pydantic import BaseModel

from app.models.schemas.core import IDMixin, DateTimeModelMixin


class RoleBase(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class RoleCreate(RoleBase):
    code: str


class RoleUpdate(RoleBase):
    pass


class Role(DateTimeModelMixin, RoleBase, IDMixin):
    class Config:
        orm_mode = True
