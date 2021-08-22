from typing import Optional, List

from pydantic import BaseModel

from app.models.domains.course import CourseType
from app.models.schemas.meeting import Meeting


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


class Course(CourseBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class CourseMeetings(CourseBase):
    id: int
    meetings: List[Meeting] = []

    class Config:
        orm_mode = True
