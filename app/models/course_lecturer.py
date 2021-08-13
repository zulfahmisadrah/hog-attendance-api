from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CourseLecturer(Base):
    semester_id = Column(ForeignKey("semester.id"), primary_key=True)
    course_id = Column(ForeignKey("course.id"), primary_key=True)
    lecturer_id = Column(ForeignKey("lecturer.id"), primary_key=True)

    semester = relationship("Semester")
    course = relationship("Course")
    lecturer = relationship("Lecturer")
