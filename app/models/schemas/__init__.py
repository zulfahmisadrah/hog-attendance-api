from .user import User, UserCreate, UserUpdate
from .role import Role, RoleCreate, RoleUpdate
from .faculty import Faculty, FacultyCreate, FacultyUpdate, FacultyDepartments
from .department import Department, DepartmentCreate, DepartmentUpdate, DepartmentCourses
from .semester import Semester, SemesterCreate, SemesterUpdate
from .schedule import Schedule, ScheduleCreate, ScheduleUpdate
from .course import Course, CourseCreate, CourseUpdate
from .token import Token, TokenPayload