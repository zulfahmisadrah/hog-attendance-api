from typing import Optional
from pydantic import BaseModel
from app.models.schemas.core import IDMixin


class StudentBase(BaseModel):
    year: Optional[int] = None


class StudentCreate(StudentBase):
    department_id: int


class StudentUpdate(StudentBase):
    department_id: Optional[int] = None
    pass


class StudentDepartment(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Student(StudentBase, IDMixin):
    department: StudentDepartment

    class Config:
        orm_mode = True
