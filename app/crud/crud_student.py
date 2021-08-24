from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash

from app import crud
from app.crud.base import CRUDBase
from app.models.domains import Student, User
from app.models.schemas.student import StudentCreate, StudentUpdate


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    def create(self, db: Session, *, obj_in: StudentCreate) -> Student:
        obj_in_data = jsonable_encoder(obj_in)
        if obj_in_data["user"]["password"]:
            hashed_password = get_password_hash(obj_in_data["user"]["password"])
            obj_in_data["user"]["password"] = hashed_password
        try:
            new_user = User(**obj_in_data["user"])
            role_student = crud.role.get(db, id=2)
            new_user.roles.append(role_student)
            new_student = Student(user_id=new_user.id, year=obj_in_data["year"], department_id=obj_in_data["department_id"])
            new_student.user = new_user
            db.add(new_user)
            db.add(new_student)
            db.commit()
            db.refresh(new_user)
        except SQLAlchemyError as e:
            print(e.args)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error Creating User")
        return new_student


student = CRUDStudent(Student)
