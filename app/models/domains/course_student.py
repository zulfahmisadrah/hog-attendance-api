from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CourseStudent(Base):
    semester_id = Column(ForeignKey("semester.id"), primary_key=True)
    course_id = Column(ForeignKey("course.id"), primary_key=True)
    student_id = Column(ForeignKey("student.id"), primary_key=True)

    semester = relationship("Semester")
    course = relationship("Course", back_populates="students")
    student = relationship("Student", back_populates="courses")

    def __init__(self, semester_id=None, course_id=None, student_id=None):
        self.semester_id = semester_id
        self.course_id = course_id
        self.student_id = student_id
