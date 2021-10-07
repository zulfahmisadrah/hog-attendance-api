from typing import List

from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase
from app.models.domains import Meeting, Attendance
from app.models.schemas.meeting import MeetingCreate, MeetingUpdate


class CRUDMeeting(CRUDBase[Meeting, MeetingCreate, MeetingUpdate]):
    def get_meeting_attendances(self, db: Session, *, meeting_id: int) -> List[Attendance]:
        attendances = crud.attendance.get_attendances_by_meeting_id(db, meeting_id=meeting_id)
        if not attendances:
            meeting_data = super().get(db, meeting_id)
            course_id = meeting_data.course.id
            active_semester = crud.semester.get_active_semester(db)
            course_students = crud.course.get_course_students(db, course_id=course_id, semester_id=active_semester.id)
            for course_student in course_students:
                attendance = Attendance(meeting_id=meeting_id, student_id=course_student.student.id)
                db.add(attendance)
            db.commit()
            attendances = crud.attendance.get_attendances_by_meeting_id(db, meeting_id=meeting_id)
        return attendances


meeting = CRUDMeeting(Meeting)
