from typing import Optional
from pydantic import BaseModel
from app.models.schemas.core import IDMixin


class StudentBase(BaseModel):
    year: Optional[int] = None
    department_id: Optional[int] = None


class StudentCreate(StudentBase):
    department_id: int


class StudentUpdate(StudentBase):
    pass


class Student(StudentBase, IDMixin):
    class Config:
        orm_mode = True
