from typing import Optional

from pydantic import BaseModel

from app.models.schemas import User, UserCreate, UserUpdate


class LecturerBase(BaseModel):
    nip: Optional[str] = None
    last_education: Optional[str] = None
    department_id: Optional[int] = None


class LecturerCreate(LecturerBase):
    user: UserCreate
    department_id: int


class LecturerUpdate(LecturerBase):
    user: Optional[UserUpdate] = None


class Lecturer(LecturerBase):
    id: Optional[int] = None
    user: User

    class Config:
        orm_mode = True

