from typing import Optional

from pydantic import BaseModel

from app.models.domains.attendance import AttendanceStatus
from app.models.schemas.core import DateTimeModelMixin, IDMixin


class AttendanceBase(BaseModel):
    status: Optional[AttendanceStatus] = None
    note: Optional[str] = None
    meeting_id: Optional[int] = None
    student_id: Optional[int] = None


class AttendanceCreate(AttendanceBase):
    status: int
    note: str
    meeting_id: int
    student_id: int


class AttendanceUpdate(AttendanceBase):
    pass


class Attendance(DateTimeModelMixin, AttendanceBase, IDMixin):
    class Config:
        orm_mode = True

