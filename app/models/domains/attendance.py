from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, BigInteger, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .meeting import Meeting
    from .student import Student


class AttendanceStatus(str, Enum):
    ABSENT = "Tanpa Keterangan"
    PRESENT = "Hadir"
    EXCUSED = "Izin"
    SICK = "Sakit"


class Attendance(Base, CommonModel):
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.ABSENT)
    note = Column(String(255))

    meeting_id = Column(BigInteger, ForeignKey("meeting.id"))
    meeting = relationship("Meeting", back_populates="attendances")

    student_id = Column(BigInteger, ForeignKey("student.id"))
    student = relationship("Student")
