from typing import Optional, List
from pydantic import BaseModel


class MeetingBase(BaseModel):
    name: Optional[str] = None
    number: Optional[int] = None
    course_id: Optional[int] = None
    schedule_id: Optional[int] = None


class MeetingCreate(MeetingBase):
    name: str
    number: int
    course_id: int
    schedule_id: int


class MeetingUpdate(MeetingBase):
    pass


class Meeting(MeetingBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

