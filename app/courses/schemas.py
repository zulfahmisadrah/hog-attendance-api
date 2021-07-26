from typing import List, Optional
from pydantic import BaseModel


class CourseBase(BaseModel):
    name: str
    sks: int
    schedule: str
    room: Optional[str] = None
    department_id: int


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: int

    class Config:
        orm_mode = True


class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    pass


class Department(DepartmentBase):
    id: int
    faculty_id: int
    courses: List[Course] = []

    class Config:
        orm_mode = True


class FacultyBase(BaseModel):
    name: str


class FacultyCreate(FacultyBase):
    pass


class Faculty(FacultyBase):
    id: int

    class Config:
        orm_mode = True


class FacultyDepartments(FacultyBase):
    id: int
    departments: List[Department] = []

    class Config:
        orm_mode = True

