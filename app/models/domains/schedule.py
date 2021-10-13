from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Time, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .meeting import Meeting


class DayOfWeek(int, Enum):
    Senin = 1
    Selasa = 2
    Rabu = 3
    Kamis = 4
    Jumat = 5
    Sabtu = 6
    Minggu = 7


class Schedule(Base, CommonModel):
    day_of_week = Column(SQLEnum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    meetings = relationship("Meeting", back_populates="schedule")
