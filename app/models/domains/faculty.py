from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel

if TYPE_CHECKING:
    from .department import Department


class Faculty(Base, CommonModel):
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(3), unique=True, nullable=False)
    alias = Column(String(10))

    departments = relationship("Department", back_populates="faculty")
