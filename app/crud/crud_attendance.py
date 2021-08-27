from app.crud.base import CRUDBase
from app.models.domains import Attendance
from app.models.schemas.attendance import AttendanceCreate, AttendanceUpdate


class CRUDAttendance(CRUDBase[Attendance, AttendanceCreate, AttendanceUpdate]):
    pass


attendance = CRUDAttendance(Attendance)
