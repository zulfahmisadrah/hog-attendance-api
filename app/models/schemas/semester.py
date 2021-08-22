from typing import Optional

from pydantic import BaseModel

from app.models.domains.semester import SemesterType


class SemesterBase(BaseModel):
    year: Optional[int] = None
    type: Optional[SemesterType] = None
    code: Optional[str] = None
    academic_year: Optional[str] = None
    is_active: Optional[bool] = False


class SemesterCreate(SemesterBase):
    year: int
    type: SemesterType


class SemesterUpdate(SemesterBase):
    pass


class Semester(SemesterBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

