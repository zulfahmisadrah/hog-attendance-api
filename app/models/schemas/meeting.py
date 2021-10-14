from datetime import date
from typing import Optional, Union

from pydantic import BaseModel

from .schedule import ScheduleSimple
from .core import DateTimeModelMixin, IDMixin


class MeetingBase(BaseModel):
    name: Optional[str] = None
    number: Optional[int] = None
    date: Optional[Union[date, str]]


class MeetingCreate(MeetingBase):
    date: Union[date, str]
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
    schedule: ScheduleSimple

    class Config:
        orm_mode = True
