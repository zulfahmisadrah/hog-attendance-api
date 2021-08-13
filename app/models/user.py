from sqlalchemy import Column, String, Boolean

from app.db.base_class import Base
from .core import CommonModel


class User(Base, CommonModel):
    username = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone_number = Column(String(15))
    avatar = Column(String(255))
    is_active = Column(Boolean(), default=True)
