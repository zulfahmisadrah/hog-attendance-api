from typing import Optional, List

from pydantic import BaseModel

from app.models.schemas.course import Course
from app.models.schemas.core import DateTimeModelMixin, IDMixin


class DepartmentBase(BaseModel):
    name: str
    code: str = None
    faculty_id: int


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = None
    code: Optional[str] = None
    faculty_id: Optional[int] = None


class Department(DateTimeModelMixin, DepartmentBase, IDMixin):
    class Config:
        orm_mode = True


class DepartmentCourses(DateTimeModelMixin, DepartmentBase, IDMixin):
    courses: List[Course] = []

    class Config:
        orm_mode = True
