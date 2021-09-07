from typing import Optional

from pydantic import BaseModel

from app.models.schemas.core import IDMixin, DateTimeModelMixin


class RoleBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class Role(DateTimeModelMixin, RoleBase, IDMixin):
    class Config:
        orm_mode = True
