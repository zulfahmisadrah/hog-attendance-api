from typing import TYPE_CHECKING

from sqlalchemy import Column, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .course_student import CourseStudent


class Student(Base, CommonModel):
    user_id = Column(BigInteger, ForeignKey("user.id"))
    user = relationship("User", backref=backref("student", uselist=False, cascade="all,delete"))

    year = Column(Integer)

    department_id = Column(BigInteger, ForeignKey("department.id"))
    department = relationship("Department")

    courses = relationship("CourseStudent", back_populates="student")
