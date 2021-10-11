from typing import Optional

from pydantic import BaseModel

from app.models.schemas.core import DateTimeModelMixin, IDMixin


class FacultyBase(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    code: Optional[str] = None


class FacultyCreate(FacultyBase):
    name: str
    code: str


class FacultyUpdate(FacultyBase):
    pass


class FacultySimple(IDMixin):
    name: Optional[str] = None

    class Config:
        orm_mode = True


class Faculty(DateTimeModelMixin, FacultyBase, IDMixin):
    class Config:
        orm_mode = True
