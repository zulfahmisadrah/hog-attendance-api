from sqlalchemy import Column, ForeignKey, Table

from app.db.base_class import Base


user_role = Table('user_role', Base.metadata,
                  Column("user_id", ForeignKey("user.id"), primary_key=True),
                  Column("role_id", ForeignKey("role.id"), primary_key=True)
                  )
