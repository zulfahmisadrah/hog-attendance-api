from typing import Optional

from pydantic import BaseModel

from app.models.domains.semester import SemesterType
from app.models.schemas.core import IDMixin, DateTimeModelMixin


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


class Semester(DateTimeModelMixin, SemesterBase, IDMixin):
    class Config:
        orm_mode = True


class SemesterSimple(IDMixin):
    academic_year: Optional[str] = None
    type: Optional[SemesterType] = None

    class Config:
        orm_mode = True
