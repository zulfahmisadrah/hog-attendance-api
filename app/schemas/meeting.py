from typing import Optional, List
from pydantic import BaseModel


class MeetingBase(BaseModel):
    name: str
    sks: int
    schedule: str
    department_id: int


class MeetingCreate(MeetingBase):
    pass


class Meeting(MeetingBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

