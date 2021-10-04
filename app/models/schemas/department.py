from typing import Optional

from pydantic import BaseModel

from .faculty import Faculty
from .core import DateTimeModelMixin, IDMixin


class DepartmentBase(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    code: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    name: str
    code: str
    faculty_id: int


class DepartmentUpdate(DepartmentBase):
    faculty_id: Optional[int] = None
    pass


class DepartmentSimple(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Department(DateTimeModelMixin, DepartmentBase, IDMixin):
    faculty: Faculty
    
    class Config:
        orm_mode = True
