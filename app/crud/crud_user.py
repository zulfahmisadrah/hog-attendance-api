from typing import Optional, Union, Dict, Any

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.resources import strings
from app.resources.enums import RoleEnum
from app.crud import crud_role
from app.crud.base import CRUDBase
from app.models.domains import User, Student, Lecturer
from app.models.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        obj_in_data = jsonable_encoder(obj_in, exclude={"roles"})
        if obj_in_data["password"]:
            hashed_password = get_password_hash(obj_in_data["password"])
            obj_in_data["password"] = hashed_password
        try:
            list_roles = jsonable_encoder(obj_in.roles)
            new_user = User(**obj_in_data)
            for role in list_roles:
                if role.get("code"):
                    user_role = crud_role.role.get_by_code(db, code=role.get("code"))
                else:
                    user_role = crud_role.role.get(db, id=role.get("id"))
                if user_role is not None:
                    new_user.roles.append(user_role)
                else:
                    print(obj_in, user_role)
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=strings.ROLE_INVALID)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            for role in new_user.roles:
                if role.code == RoleEnum.STUDENT.value:
                    student = Student(user_id=new_user.id)
                    db.add(student)
                elif role.code == RoleEnum.LECTURER.value:
                    lecturer = Lecturer(user_id=new_user.id)
                    db.add(lecturer)
            db.commit()
        except SQLAlchemyError as e:
            print(e.args)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=strings.ERROR_INTERNAL_SERVER_ERROR)
        return new_user

    def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        elif not verify_password(password, user.password):
            return None
        return user

    def is_active(self, user: User):
        return user.is_active

    def is_superuser(self, user: User):
        list_user_roles = [role_dict.code for role_dict in user.roles]
        is_superuser = False
        if "ROLE_SUPERUSER" in list_user_roles:
            is_superuser = True
        return is_superuser

    def is_admin(self, user: User):
        list_user_roles = [role_dict.code for role_dict in user.roles]
        is_admin = False
        if "ROLE_SUPERUSER" in list_user_roles or "ROLE_ADMIN" in list_user_roles:
            is_admin = True
        return is_admin


user = CRUDUser(User)
