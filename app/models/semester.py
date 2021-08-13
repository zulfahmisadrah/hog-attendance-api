from enum import Enum

from sqlalchemy import Column, String, Integer, Enum as SQLEnum, Boolean

from app.db.base_class import Base
from .core import BlameModel


class SemesterType(str, Enum):
    ODD = "Ganjil"
    EVEN = "Genap"


class Semester(Base, BlameModel):
    year = Column(Integer, nullable=False)
    type = Column(SQLEnum(SemesterType), nullable=False)
    code = Column(String(5))
    academic_year = Column(String(9))
    is_active = Column(Boolean(), default=True)
