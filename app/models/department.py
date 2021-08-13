from typing import TYPE_CHECKING

from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .faculty import Faculty
    from .course import Course


class Department(Base, CommonModel):
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(3), unique=True, nullable=False)

    faculty_id = Column(BigInteger, ForeignKey("faculty.id"))
    faculty = relationship("Faculty", back_populates="departments")

    courses = relationship("Course", back_populates="department")
