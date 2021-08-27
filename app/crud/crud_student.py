from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash

from app import crud
from app.crud.base import CRUDBase
from app.models.domains import Student, User
from app.models.schemas.student import StudentCreate, StudentUpdate
from app.resources import strings


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    def create(self, db: Session, *, obj_in: StudentCreate) -> Student:
        obj_in_data = jsonable_encoder(obj_in)
        if obj_in_data["user"]["password"]:
            hashed_password = get_password_hash(obj_in_data["user"]["password"])
            obj_in_data["user"]["password"] = hashed_password
        try:
            new_user = User(**obj_in_data["user"])
            role_student = crud.role.get(db, id=4)
            new_user.roles.append(role_student)
            del obj_in_data["user"]
            new_student = Student(user=new_user, **obj_in_data)
            new_student.user = new_user
            db.add(new_student)
            db.commit()
            db.refresh(new_student)
        except SQLAlchemyError as e:
            print(e.args)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=strings.ERROR_INTERNAL_SERVER_ERROR)
        return new_student

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
