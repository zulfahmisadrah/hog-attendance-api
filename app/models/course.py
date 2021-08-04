from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .department import Department


class Course(Base, CommonModel):
    name = Column(String(50), nullable=False)
    sks = Column(Integer, nullable=False)
    schedule = Column(String(20), nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"))
    department = relationship("Department", back_populates="courses")
