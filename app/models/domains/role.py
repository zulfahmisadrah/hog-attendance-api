from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .core import CommonModel
from .user_role import user_role


class Role(Base, CommonModel):
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))

    users = relationship("User", secondary=user_role, back_populates="roles", cascade="all, delete")

    def __str__(self):
        return str(self.__dict__)
