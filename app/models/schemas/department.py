from typing import Optional, List

from pydantic import BaseModel, Field

# from .course import Course
from app.models.schemas.core import DateTimeModelMixin, IDMixin


class DepartmentBase(BaseModel):
    name: Optional[str] = None
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
    class Config:
        orm_mode = True
#
#
# class DepartmentCourses(DateTimeModelMixin, DepartmentBase, IDMixin):
#     courses: List[Course] = []
#
#     class Config:
#         orm_mode = True
