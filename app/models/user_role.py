from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class UserRole(Base):
    user_id = Column(BigInteger, ForeignKey("user.id"), primary_key=True)
    role_id = Column(BigInteger, ForeignKey("role.id"), primary_key=True)

    user = relationship("User", backref="roles")
    role = relationship("Role", backref="users")
