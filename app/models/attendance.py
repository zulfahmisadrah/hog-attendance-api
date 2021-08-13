from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, BigInteger, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .meeting import Meeting
    from .user import User


class AttendanceStatus(str, Enum):
    ABSENT = "Tanpa Keterangan"
    PRESENT = "Hadir"
    EXCUSED = "Izin"
    SICK = "Sakit"


class Attendance(Base, CommonModel):
    name = Column(String(50))
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.ABSENT)

    meeting_id = Column(BigInteger, ForeignKey("meeting.id"))
    meeting = relationship("Meeting", back_populates="attendances")

    student_id = Column(BigInteger, ForeignKey("student.id"))
    student = relationship("Student")
