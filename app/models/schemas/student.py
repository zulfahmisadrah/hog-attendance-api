from typing import Optional

from pydantic import BaseModel

from app.models.schemas import User, UserCreate, UserUpdate


class StudentBase(BaseModel):
    year: Optional[int] = None
    user: Optional[int] = None
    department_id: Optional[int] = None


class StudentCreate(StudentBase):
    user: UserCreate
    department_id: int


class StudentUpdate(StudentBase):
    user: Optional[UserUpdate] = None


class Student(StudentBase):
    id: Optional[int] = None
    user: User

    class Config:
        orm_mode = True

