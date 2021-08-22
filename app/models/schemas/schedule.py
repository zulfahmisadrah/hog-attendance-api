from typing import Optional
from datetime import time
from pydantic import BaseModel

from app.models.domains.schedule import DayOfWeek


class ScheduleBase(BaseModel):
    day_of_week: Optional[DayOfWeek] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class ScheduleCreate(ScheduleBase):
    day_of_week: DayOfWeek
    start_time: time
    end_time: time


class ScheduleUpdate(ScheduleBase):
    pass


class Schedule(ScheduleBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

