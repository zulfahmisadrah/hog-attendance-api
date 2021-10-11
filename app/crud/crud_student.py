from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase
from app.models.domains import User, Student, CourseStudent
from app.models.schemas import StudentUser
from app.models.schemas.user import UserStudentCreate, UserUpdate
from app.models.schemas.student import StudentCreate, StudentUpdate


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    def get_by_username_or_name(self, db: Session, *, keyword: str, offset: int = 0, limit: int = 10) -> Student:
        keyword = "%{}%".format(keyword)
        return db.query(Student).join(Student.user) \
            .filter(
            or_(
                User.username.like(keyword),
                User.name.like(keyword)
            )) \
            .offset(offset).limit(limit).all()

    def get_by_name(self, db: Session, *, name: str, offset: int = 0, limit: int = 10) -> Student:
        keyword = "%{}%".format(name)
        return db.query(Student).join(Student.user) \
            .filter(User.name.like(keyword)) \
            .offset(offset).limit(limit).all()

    def get_by_department_id(self, db: Session, *, department_id: int) -> Student:
        return db.query(Student).filter(Student.department_id == department_id).all()

    def get_by_department_id_and_username_or_name(self, db: Session, *, department_id: int, keyword: str,
                                                  offset: int = 0, limit: int = 10) -> Student:
        keyword = "%{}%".format(keyword)
        return db.query(Student).join(Student.user) \
            .filter(
            Student.department_id == department_id,
            or_(
                User.username.like(keyword),
                User.name.like(keyword)
            )) \
            .order_by(User.username) \
            .offset(offset).limit(limit).all()

    def get_by_department_id_and_name(self, db: Session, *, department_id: int, name: str, offset: int = 0,
                                      limit: int = 10) -> Student:
        keyword = "%{}%".format(name)
        return db.query(Student).join(Student.user) \
            .filter(Student.department_id == department_id, User.name.like(keyword)) \
            .order_by(User.username) \
            .offset(offset).limit(limit).all()

    def get_student_courses(self, db: Session, *, student_id: int, semester_id: int) -> CourseStudent:
        return db.query(CourseStudent).filter(
            CourseStudent.semester_id == semester_id,
            CourseStudent.student_id == student_id
        ).all()

    def create(self, db: Session, *, obj_in: UserStudentCreate) -> User:
        return crud.user.create_student(db, obj_in=obj_in)

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        return crud.user.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete(self, db: Session, *, db_obj: Student) -> Any:
        user_id = db_obj.user.id
        return crud.user.delete(db, id=user_id)
        # student_data = db.query(Student).get(student_user.id)
        # return super().delete(db, id=db_obj.id)


student = CRUDStudent(Student)
