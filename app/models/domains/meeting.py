from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Date, Time, Enum as SQLEnum
from sqlalchemy.orm import relationship

from .core import CommonModel
from app.db.base_class import Base
from app.resources.enums import DayOfWeek, MeetingStatus

if TYPE_CHECKING:
    from .course import Course
    from .schedule import Schedule


class Meeting(Base, CommonModel):
    name = Column(String(50))
    number = Column(Integer)
    status = Column(SQLEnum(MeetingStatus), default=MeetingStatus.Terjadwal)
    date = Column(Date)
    day_of_week = Column(SQLEnum(DayOfWeek))
    start_time = Column(Time)
    end_time = Column(Time)

    course_id = Column(BigInteger, ForeignKey("course.id"))
    course = relationship("Course", back_populates="meetings")

    schedule_id = Column(BigInteger, ForeignKey("schedule.id"))
    schedule = relationship("Schedule", back_populates="meetings")

    attendances = relationship("Attendance", back_populates="meeting")

