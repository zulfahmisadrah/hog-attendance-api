from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CourseLecturer(Base):
    semester_id = Column(ForeignKey("semester.id"), primary_key=True)
    course_id = Column(ForeignKey("course.id"), primary_key=True)
    lecturer_id = Column(ForeignKey("lecturer.id"), primary_key=True)

    semester = relationship("Semester")
    course = relationship("Course", back_populates="lecturers")
    lecturer = relationship("Lecturer", back_populates="courses")

    def __init__(self, semester_id=None, course_id=None, lecturer_id=None):
        self.semester_id = semester_id
        self.course_id = course_id
        self.lecturer_id = lecturer_id
