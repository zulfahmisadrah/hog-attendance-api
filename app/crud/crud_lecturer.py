from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase
from app.models.domains import User, Lecturer, CourseLecturer
from app.core.security import get_password_hash
from app.models.schemas import UserLecturerCreate, LecturerUser
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

    def update(self, db: Session, *, db_obj: Lecturer, obj_in: LecturerUpdate) -> Lecturer:
        update_data = obj_in.dict(exclude_unset=True)
        update_user_data = update_data["user"]
        if update_user_data:
            if update_user_data["password"]:
                hashed_password = get_password_hash(update_user_data["password"])
                update_user_data["password"] = hashed_password
            obj_data = jsonable_encoder(update_user_data)
            for field in obj_data:
                if field in update_user_data:
                    setattr(db_obj.user, field, update_user_data[field])
            db.add(db_obj.user)
        del update_data["user"]
        return super().update(db, db_obj=db_obj, obj_in=update_data)


lecturer = CRUDLecturer(Lecturer)
