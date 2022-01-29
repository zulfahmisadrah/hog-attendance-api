from typing import List

from sqlalchemy.orm import Session

from app.crud import crud_meeting
from app.crud.base import CRUDBase
from app.models.domains import Attendance
from app.models.schemas.attendance import AttendanceCreate, AttendanceUpdate
from app.resources.enums import AttendanceStatus


class CRUDAttendance(CRUDBase[Attendance, AttendanceCreate, AttendanceUpdate]):
    def get_attendances_by_meeting_id(self, db: Session, *, meeting_id: int) -> List[Attendance]:
        return db.query(Attendance).filter_by(meeting_id=meeting_id).all()

    def get_attendances_by_student_id(self, db: Session, *, student_id: int) -> List[Attendance]:
        return db.query(Attendance).filter_by(student_id=student_id).all()

    def get_attendances_by_meeting_id_and_student_id(self, db: Session, *, meeting_id: int,
                                                     student_id: int) -> Attendance:
        return db.query(Attendance).filter_by(meeting_id=meeting_id, student_id=student_id).first()

    def get_course_attendances(self, db: Session, *, course_id: int) -> List[Attendance]:
        meetings = crud_meeting.meeting.get_meetings_by_course_id(db, course_id=course_id)
        attendances = [meeting.attendance for meeting in meetings]
        return attendances

    def reset_attendance_validate(self, db: Session, *, meeting_id: int):
        attendances = self.get_attendances_by_meeting_id(db, meeting_id=meeting_id)
        for attendance_data in attendances:
            db.query(Attendance).filter_by(id=attendance_data.id).update({'status_validate': AttendanceStatus.Absen})
        db.commit()


attendance = CRUDAttendance(Attendance)
