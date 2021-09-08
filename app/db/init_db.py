from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.db.db_seeder import DBSeeder


def init_db(db: Session) -> None:
    DBSeeder(db, crud.role, schemas.RoleCreate).load_from_json("role.json")
    DBSeeder(db, crud.faculty, schemas.FacultyCreate).load_from_json("faculty.json")
    DBSeeder(db, crud.department, schemas.DepartmentCreate).load_from_json("department.json")
    DBSeeder(db, crud.semester, schemas.SemesterCreate).load_from_json("semester.json")
    DBSeeder(db, crud.user, schemas.UserRolesCreate).load_from_json("user.json")
    DBSeeder(db, crud.lecturer, schemas.UserLecturerCreate).load_from_json("lecturer.json")
    DBSeeder(db, crud.student, schemas.UserStudentCreate).load_from_json("student.json")
    DBSeeder(db, crud.schedule, schemas.ScheduleCreate).load_from_json("schedule.json")
    DBSeeder(db, crud.course, schemas.CourseCreate).load_from_json("course.json")
    DBSeeder(db, crud.meeting, schemas.MeetingCreate).load_from_json("meeting.json")

