from sqlalchemy import Column, Integer, String

from app.db.base_class import Base


class Faculty(Base):
    # __tablename__ = "faculties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
