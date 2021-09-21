from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase
from app.models.domains import Student, CourseStudent
from app.core.security import get_password_hash
from app.models.schemas import UserStudent
from app.models.schemas.student import StudentCreate, StudentUpdate
from app.models.schemas.user import UserStudentCreate


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    def get_student_courses(self, db: Session, *, student_id: int, semester_id: int) -> CourseStudent:
        return db.query(CourseStudent).filter(
            CourseStudent.semester_id == semester_id,
            CourseStudent.student_id == student_id
        ).all()

    def create(self, db: Session, *, obj_in: UserStudentCreate) -> UserStudent:
        return crud.user.create_student(db, obj_in=obj_in)

    def update(self, db: Session, *, db_obj: Student, obj_in: StudentUpdate) -> Student:
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


student = CRUDStudent(Student)
