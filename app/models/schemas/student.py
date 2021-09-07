from typing import Optional

from pydantic import BaseModel

from app.models.schemas import User, UserCreate, UserUpdate
from app.models.schemas.core import IDMixin


class StudentBase(BaseModel):
    year: Optional[int] = None
    user: Optional[int] = None
    department_id: Optional[int] = None


class StudentCreate(StudentBase):
    user: UserCreate


class StudentUpdate(StudentBase):
    user: Optional[UserUpdate] = None


class Student(StudentBase, IDMixin):
    user: User

    class Config:
        orm_mode = True

