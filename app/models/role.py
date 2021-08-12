from sqlalchemy import Column, String

from app.db.base_class import Base
from .core import CommonModel


class Role(Base, CommonModel):
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
