from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase
from app.models.domains import User, Lecturer, CourseLecturer
from app.models.schemas.user import UserLecturerCreate, UserUpdate
from app.models.schemas.lecturer import LecturerCreate, LecturerUpdate


class CRUDLecturer(CRUDBase[Lecturer, LecturerCreate, LecturerUpdate]):
    def get_by_username_or_name(self, db: Session, *, keyword: str, offset: int = 0, limit: int = 10) -> Lecturer:
        keyword = "%{}%".format(keyword)
        return db.query(Lecturer).join(Lecturer.user) \
            .filter(
            or_(
                User.username.like(keyword),
                User.name.like(keyword)
            )) \
            .offset(offset).limit(limit).all()

    def get_by_name(self, db: Session, *, name: str, offset: int = 0, limit: int = 10) -> Lecturer:
        keyword = "%{}%".format(name)
        return db.query(Lecturer).join(Lecturer.user) \
            .filter(User.name.like(keyword)) \
            .offset(offset).limit(limit).all()

    def get_by_department_id(self, db: Session, *, department_id: int) -> Lecturer:
        return db.query(Lecturer).filter(Lecturer.department_id == department_id).all()

    def get_by_department_id_and_username_or_name(self, db: Session, *, department_id: int, keyword: str,
                                                  offset: int = 0, limit: int = 10) -> Lecturer:
        keyword = "%{}%".format(keyword)
        return db.query(Lecturer).join(Lecturer.user) \
            .filter(
            Lecturer.department_id == department_id,
            or_(
                User.username.like(keyword),
                User.name.like(keyword)
            )) \
            .order_by(User.username) \
            .offset(offset).limit(limit).all()

    def get_by_department_id_and_name(self, db: Session, *, department_id: int, name: str, offset: int = 0,
                                      limit: int = 10) -> Lecturer:
        keyword = "%{}%".format(name)
        return db.query(Lecturer).join(Lecturer.user) \
            .filter(Lecturer.department_id == department_id, User.name.like(keyword)) \
            .order_by(User.username) \
            .offset(offset).limit(limit).all()

    def get_lecturer_courses(self, db: Session, *, lecturer_id: int, semester_id: int) -> CourseLecturer:
        return db.query(CourseLecturer).filter(
            CourseLecturer.semester_id == semester_id,
            CourseLecturer.lecturer_id == lecturer_id
        ).all()

    def create(self, db: Session, *, obj_in: UserLecturerCreate) -> User:
        return crud.user.create_lecturer(db, obj_in=obj_in)

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        return crud.user.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete(self, db: Session, *, db_obj: Lecturer) -> Any:
        user_id = db_obj.user.id
        return crud.user.delete(db, id=user_id)


lecturer = CRUDLecturer(Lecturer)
