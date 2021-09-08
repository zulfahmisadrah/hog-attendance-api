from typing import Optional
from pydantic import BaseModel
from app.models.schemas.core import IDMixin


class LecturerBase(BaseModel):
    nip: Optional[str] = None
    last_education: Optional[str] = None
    department_id: Optional[int] = None


class LecturerCreate(LecturerBase):
    department_id: int


class LecturerUpdate(LecturerBase):
    pass


class Lecturer(LecturerBase, IDMixin):
    class Config:
        orm_mode = True
