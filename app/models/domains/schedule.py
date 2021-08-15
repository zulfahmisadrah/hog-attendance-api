from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Time, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .meeting import Meeting


class DayOfWeek(int, Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7


class Schedule(Base, CommonModel):
    day_of_week = Column(SQLEnum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    meetings = relationship("Meeting", back_populates="schedule")
