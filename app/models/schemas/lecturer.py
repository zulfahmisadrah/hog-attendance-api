from typing import Optional

from pydantic import BaseModel

from app.models.schemas import User, UserCreate, UserUpdate
from app.models.schemas.core import IDMixin, DateTimeModelMixin


class LecturerBase(BaseModel):
    nip: Optional[str] = None
    last_education: Optional[str] = None
    department_id: Optional[int] = None


class LecturerCreate(LecturerBase):
    user: UserCreate


class LecturerUpdate(LecturerBase):
    user: Optional[UserUpdate] = None


class Lecturer(DateTimeModelMixin, LecturerBase, IDMixin):
    user: User

    class Config:
        orm_mode = True
