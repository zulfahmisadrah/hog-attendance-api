from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase
from app.models.domains import Meeting, Attendance
from app.models.schemas.meeting import MeetingCreate, MeetingUpdate
from app.resources.enums import MeetingStatus


class CRUDMeeting(CRUDBase[Meeting, MeetingCreate, MeetingUpdate]):
    def get_meeting_attendances(self, db: Session, *, meeting_id: int) -> List[Attendance]:
        meeting_data = super().get(db, meeting_id)
        course_id = meeting_data.course.id
        active_semester = crud.semester.get_active_semester(db)
        course_students = crud.course.get_course_students(db, course_id=course_id, semester_id=active_semester.id)
        attendances = crud.attendance.get_attendances_by_meeting_id(db, meeting_id=meeting_id)
        attendances_student_id = [attendance.student.id for attendance in attendances]
        if not attendances or len(attendances) != len(course_students):
            for course_student in course_students:
                student_id = course_student.student.id
                if student_id not in attendances_student_id:
                    attendance = Attendance(meeting_id=meeting_id, student_id=student_id)
                    db.add(attendance)
            db.commit()
            attendances = crud.attendance.get_attendances_by_meeting_id(db, meeting_id=meeting_id)
        return attendances

    def get_meeting_today(self, db: Session):
        current_datetime = datetime.now()
        return db.query(Meeting).filter(Meeting.date == current_datetime.date()).all()

    def update_meetings_status(self, db: Session, meetings: List[Meeting]):
        current_datetime = datetime.now()
        for meeting_data in meetings:
            start_time = meeting_data.start_time if meeting_data.start_time else meeting_data.schedule.start_time
            end_time = meeting_data.end_time if meeting_data.end_time else meeting_data.schedule.end_time
            attendance_open_time = (datetime.combine(meeting_data.date, start_time) - timedelta(minutes=15))
            attendance_close_time = (datetime.combine(meeting_data.date, end_time) + timedelta(minutes=30))
            if current_datetime.date() == meeting_data.date \
                    and attendance_open_time.time() <= current_datetime.time() < attendance_close_time.time() \
                    and meeting_data.status is not MeetingStatus.Berlangsung:
                meeting_status = MeetingStatus.Berlangsung
            elif current_datetime.date() <= meeting_data.date \
                    and current_datetime.time() < attendance_open_time.time() \
                    and meeting_data.status is not MeetingStatus.Terjadwal:
                meeting_status = MeetingStatus.Terjadwal
            elif current_datetime.date() >= meeting_data.date \
                    and current_datetime.time() >= attendance_close_time.time() \
                    and meeting_data.status is not MeetingStatus.Selesai:
                meeting_status = MeetingStatus.Selesai
            else:
                meeting_status = meeting_data.status

            if meeting_data.status != meeting_status:
                db.query(Meeting).filter(Meeting.id == meeting_data.id).update({Meeting.status: meeting_status})
        db.commit()


meeting = CRUDMeeting(Meeting)
