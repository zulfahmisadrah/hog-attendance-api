from typing import TYPE_CHECKING

from sqlalchemy import Column, BigInteger, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel
from app.resources.enums import AttendanceStatus

if TYPE_CHECKING:
    from .meeting import Meeting
    from .student import Student


class Attendance(Base, CommonModel):
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.Absen)
    status_validate = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.Absen)
    status_by_student = Column(SQLEnum(AttendanceStatus))
    note = Column(String(255))

    meeting_id = Column(BigInteger, ForeignKey("meeting.id"))
    meeting = relationship("Meeting", back_populates="attendances")

    student_id = Column(BigInteger, ForeignKey("student.id"))
    student = relationship("Student")
