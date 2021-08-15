from typing import Optional, List

from pydantic import BaseModel

from app.models.schemas.meeting import Meeting


class CourseBase(BaseModel):
    name: str
    code: str
    sks: int
    department_id: int


class CourseCreate(CourseBase):
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
