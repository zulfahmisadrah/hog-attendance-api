from typing import Optional
from pydantic import BaseModel
from app.models.schemas.core import IDMixin
from .faculty import FacultySimple


class StudentBase(BaseModel):
    year: Optional[int] = None


class StudentCreate(StudentBase):
    department_id: int


class StudentUpdate(StudentBase):
    department_id: Optional[int] = None


class StudentDepartment(BaseModel):
    id: int
    name: str
    faculty: FacultySimple

    class Config:
        orm_mode = True


class Student(StudentBase, IDMixin):
    department: StudentDepartment

    class Config:
        orm_mode = True
