from typing import Optional
from pydantic import BaseModel
from app.models.schemas.core import IDMixin
from .faculty import FacultySimple


class LecturerBase(BaseModel):
    nip: Optional[str] = None
    last_education: Optional[str] = None


class LecturerCreate(LecturerBase):
    department_id: int


class LecturerUpdate(LecturerBase):
    department_id: Optional[int] = None


class LecturerDepartment(BaseModel):
    id: int
    name: str
    faculty: FacultySimple

    class Config:
        orm_mode = True


class Lecturer(LecturerBase, IDMixin):
    department: LecturerDepartment

    class Config:
        orm_mode = True
