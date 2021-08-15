from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base
from .core import CommonModel
from .user_role import user_role


class User(Base, CommonModel):
    username = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone_number = Column(String(15))
    avatar = Column(String(255))
    is_active = Column(Boolean(), default=True)

    role = relationship("Role", secondary=user_role, backref="users", lazy="dynamic")

    def __str__(self):
        return str(self.__dict__)
