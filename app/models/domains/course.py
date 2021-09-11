from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .department import Department
    from .meeting import Meeting
    from .course_student import CourseStudent
    from .course_lecturer import CourseLecturer


class CourseType(str, Enum):
    WAJIB = "Wajib"
    PILIHAN = "Pilihan"


class Course(Base, CommonModel):
    name = Column(String(50), nullable=False)
    code = Column(String(15), unique=True, nullable=False)
    sks = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    quota = Column(Integer, nullable=False)
    type = Column(SQLEnum(CourseType), default=CourseType.WAJIB)

    department_id = Column(BigInteger, ForeignKey("department.id"))
    department = relationship("Department", back_populates="courses")

    meetings = relationship("Meeting", back_populates="course")
    students = relationship("CourseStudent", back_populates="course")
    lecturers = relationship("CourseLecturer", back_populates="course")
