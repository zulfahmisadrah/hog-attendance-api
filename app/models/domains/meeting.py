from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .course import Course
    from .schedule import Schedule


class Meeting(Base, CommonModel):
    name = Column(String(50))
    number = Column(Integer)
    date = Column(Date)

    course_id = Column(BigInteger, ForeignKey("course.id"))
    course = relationship("Course", back_populates="meetings")

    schedule_id = Column(BigInteger, ForeignKey("schedule.id"))
    schedule = relationship("Schedule", back_populates="meetings")

    attendances = relationship("Attendance", back_populates="meeting")

