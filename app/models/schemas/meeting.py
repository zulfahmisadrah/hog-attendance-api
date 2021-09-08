from typing import Optional

from pydantic import BaseModel

from .schedule import Schedule
from .core import DateTimeModelMixin, IDMixin


class MeetingBase(BaseModel):
    name: Optional[str] = None
    number: Optional[int] = None
    date: Optional[str] = None


class MeetingCreate(MeetingBase):
    name: str
    number: int
    date: str
    course_id: int
    schedule_id: int


class MeetingUpdate(MeetingBase):
    course_id: Optional[int] = None
    schedule_id: Optional[int] = None


class MeetingCourse(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None

    class Config:
        orm_mode = True


class Meeting(DateTimeModelMixin, MeetingBase, IDMixin):
    course: MeetingCourse
    schedule: Schedule

    class Config:
        orm_mode = True
