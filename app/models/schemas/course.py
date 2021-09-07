from typing import Optional, List

from pydantic import BaseModel

from app.models.domains.course import CourseType
from app.models.schemas.core import DateTimeModelMixin, IDMixin


class CourseBase(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    sks: Optional[int] = None
    semester: Optional[int] = None
    quota: Optional[int] = None
    type: CourseType
    department_id: int


class CourseCreate(CourseBase):
    name: str
    code: str
    sks: int
    semester: int
    quota: int


class CourseUpdate(CourseBase):
    pass


class Course(DateTimeModelMixin, CourseBase, IDMixin):
    class Config:
        orm_mode = True


class CourseMeetings(DateTimeModelMixin, CourseBase, IDMixin):
    meetings: "List[Meeting]" = []

    class Config:
        orm_mode = True
