from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.domains import Attendance
from app.models.schemas.attendance import AttendanceCreate, AttendanceUpdate


class CRUDAttendance(CRUDBase[Attendance, AttendanceCreate, AttendanceUpdate]):
    def get_attendances_by_meeting_id(self, db: Session, *, meeting_id: int):
        return db.query(Attendance).filter_by(meeting_id=meeting_id).all()


attendance = CRUDAttendance(Attendance)
