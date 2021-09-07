from typing import Optional, List

from pydantic import BaseModel

from app.models.schemas.core import DateTimeModelMixin, IDMixin
from app.models.schemas.department import Department


class FacultyBase(BaseModel):
    name: str
    code: str


class FacultyCreate(FacultyBase):
    pass


class FacultyUpdate(FacultyBase):
    name: Optional[str] = None
    code: Optional[str] = None


class Faculty(DateTimeModelMixin, FacultyBase, IDMixin):
    class Config:
        orm_mode = True


class FacultyDepartments(DateTimeModelMixin, FacultyBase, IDMixin):
    departments: List[Department] = []

    class Config:
        orm_mode = True
