from typing import Optional, List

from pydantic import BaseModel, EmailStr

from .lecturer import LecturerCreate, LecturerUpdate, Lecturer
from .student import StudentCreate, StudentUpdate, Student
from .core import DateTimeModelMixin, IDMixin


class UserRole(BaseModel):
    id: Optional[int] = None
    code: Optional[str] = None

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    name: str
    username: str
    password: str


class UserStudentCreate(UserCreate):
    student: StudentCreate


class UserLecturerCreate(UserCreate):
    lecturer: LecturerCreate


class UserRolesCreate(UserCreate):
    roles: List[int] = []


class UserUpdate(UserBase):
    password: Optional[str] = None
    student: Optional[StudentUpdate] = None
    lecturer: Optional[LecturerUpdate] = None


class User(DateTimeModelMixin, UserBase, IDMixin):
    roles: List[UserRole] = []

    class Config:
        orm_mode = True


class UserSimple(IDMixin):
    username: Optional[str] = None
    name: Optional[str] = None

    class Config:
        orm_mode = True


class UserStudent(User):
    student: Student


class UserLecturer(User):
    lecturer: Lecturer


class LecturerUser(DateTimeModelMixin, Lecturer, IDMixin):
    user: UserSimple

    class Config:
        orm_mode = True


class StudentUser(DateTimeModelMixin, Student, IDMixin):
    user: UserSimple

    class Config:
        orm_mode = True
