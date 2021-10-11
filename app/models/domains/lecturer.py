from typing import TYPE_CHECKING

from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .course_lecturer import CourseLecturer


class Lecturer(Base, CommonModel):
    user_id = Column(BigInteger, ForeignKey("user.id"))
    user = relationship("User", backref=backref("lecturer", uselist=False, cascade="all,delete"))

    nip = Column(String(20))
    last_education = Column(String(10))

    department_id = Column(BigInteger, ForeignKey("department.id"))
    department = relationship("Department")

    courses = relationship("CourseLecturer", back_populates="lecturer")
