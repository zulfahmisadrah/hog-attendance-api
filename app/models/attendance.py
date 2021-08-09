from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .meeting import Meeting
    from .user import User


class AttendanceStatus(str, Enum):
    ABSENT = "ABSENT"
    PRESENT = "PRESENT"
    EXCUSED = "EXCUSED"
    SICK = "SICK"


class Attendance(Base, CommonModel):
    name = Column(String(50))
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.ABSENT)

    meeting_id = Column(Integer, ForeignKey("meeting.id"))
    meeting = relationship("Meeting", back_populates="attendances")

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="attendances")
