from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase
from app.models.domains import Lecturer
from app.core.security import get_password_hash
from app.models.schemas import User, UserLecturerCreate
from app.models.schemas.lecturer import LecturerCreate, LecturerUpdate


class CRUDLecturer(CRUDBase[Lecturer, LecturerCreate, LecturerUpdate]):
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
