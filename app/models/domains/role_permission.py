from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RolePermission(Base):
    role_id = Column(BigInteger, ForeignKey("role.id"), primary_key=True)
    permission_id = Column(BigInteger, ForeignKey("permission.id"), primary_key=True)

    role = relationship("Role", backref="permissions")
    permission = relationship("Permission", backref="roles")
