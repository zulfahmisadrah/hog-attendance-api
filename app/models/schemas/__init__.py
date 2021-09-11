from .user import User, UserCreate, UserUpdate, UserStudent, UserStudentCreate, UserLecturer, UserLecturerCreate, UserRolesCreate, LecturerUser, StudentUser
from .role import Role, RoleCreate, RoleUpdate
from .student import Student, StudentCreate, StudentUpdate
from .lecturer import Lecturer, LecturerCreate, LecturerUpdate
from .faculty import Faculty, FacultyCreate, FacultyUpdate, FacultyDepartments
from .department import Department, DepartmentCreate, DepartmentUpdate, DepartmentCourses
from .semester import Semester, SemesterCreate, SemesterUpdate
from .schedule import Schedule, ScheduleCreate, ScheduleUpdate
from .course import Course, CourseCreate, CourseUpdate, CourseLecturers, CourseStudents, LecturerCourses, StudentCourses
from .meeting import Meeting, MeetingCreate, MeetingUpdate
from .attendance import Attendance, AttendanceCreate, AttendanceUpdate
from .token import Token, TokenPayload
