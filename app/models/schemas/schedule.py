from typing import Optional
from datetime import time
from pydantic import BaseModel

from app.models.domains.schedule import DayOfWeek
from app.models.schemas.core import IDMixin, DateTimeModelMixin


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


class ScheduleSimple(ScheduleBase, IDMixin):
    class Config:
        orm_mode = True


class Schedule(DateTimeModelMixin, ScheduleBase, IDMixin):
    class Config:
        orm_mode = True
