from typing import Optional

from pydantic import BaseModel

from app.models.domains.attendance import AttendanceStatus
from app.models.schemas import Meeting, StudentUserSimple
from app.models.schemas.core import DateTimeModelMixin, IDMixin


class AttendanceBase(BaseModel):
    status: AttendanceStatus = AttendanceStatus.ABSEN
    note: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    meeting_id: int
    student_id: int


class AttendanceUpdate(AttendanceBase):
    pass


class Attendance(DateTimeModelMixin, AttendanceBase, IDMixin):
    meeting: Meeting
    student: StudentUserSimple

    class Config:
        orm_mode = True

