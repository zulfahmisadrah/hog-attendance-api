from typing import Optional, Union
from datetime import date, time

from pydantic import BaseModel

from .schedule import ScheduleSimple
from .core import DateTimeModelMixin, IDMixin
from app.resources.enums import DayOfWeek, MeetingStatus


class MeetingBase(BaseModel):
    name: Optional[str] = None
    number: Optional[int] = None
    date: Optional[Union[date, str]]
    status: Optional[MeetingStatus] = None
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


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
