from typing import Optional, List

from pydantic import BaseModel

from .department import DepartmentSimple
from .user import LecturerUser, StudentUserSimple
from .semester import SemesterSimple
from app.models.domains.course import CourseType
from app.models.schemas.core import DateTimeModelMixin, IDMixin


class CourseBase(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    sks: Optional[int] = None
    semester: Optional[int] = None
    quota: Optional[int] = None
    type: CourseType


class CourseCreate(CourseBase):
    name: str
    code: str
    sks: int
    semester: int
    quota: int
    lecturers: List[int] = []
    students: List[int] = []
    department_id: int


class CourseUpdate(CourseBase):
    department_id: Optional[int] = None


class Course(DateTimeModelMixin, CourseBase, IDMixin):
    department: DepartmentSimple

    class Config:
        orm_mode = True


class CourseSimple(IDMixin):
    name: Optional[str] = None

    class Config:
        orm_mode = True


class CourseMeetings(DateTimeModelMixin, CourseBase, IDMixin):
    meetings: "List[Meeting]" = []

    class Config:
        orm_mode = True


class CourseLecturers(BaseModel):
    lecturers: List[LecturerUser]
    course: CourseSimple
    semester: SemesterSimple

    class Config:
        orm_mode = True


class CourseStudents(BaseModel):
    students: List[StudentUserSimple]
    course: CourseSimple
    semester: SemesterSimple

    class Config:
        orm_mode = True


class LecturerCourses(BaseModel):
    courses: List[Course]
    semester: SemesterSimple
    lecturer: LecturerUser

    class Config:
        orm_mode = True


class StudentCourses(BaseModel):
    courses: List[Course]
    semester: SemesterSimple
    student: StudentUserSimple

    class Config:
        orm_mode = True
