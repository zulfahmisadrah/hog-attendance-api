from typing import Optional, List

from pydantic import BaseModel

from app.models.schemas.course import Course


class DepartmentBase(BaseModel):
    name: str
    code: str = None
    faculty_id: int


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = None
    code: Optional[str] = None
    faculty_id: Optional[str] = None


class Department(DepartmentBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class DepartmentCourses(DepartmentBase):
    id: int
    courses: List[Course] = []

    class Config:
        orm_mode = True
