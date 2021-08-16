from typing import Optional, Union, Dict, Any

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud import crud_role
from app.crud.base import CRUDBase
from app.models.domains import User
from app.models.schemas import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate, role_id: int) -> User:
        obj_in_data = jsonable_encoder(obj_in)
        if obj_in_data["password"]:
            hashed_password = get_password_hash(obj_in_data["password"])
            obj_in_data["password"] = hashed_password
        try:
            new_user = User(**obj_in_data)
            role_superuser = crud_role.role.get(db, id=role_id)
            new_user.roles.append(role_superuser)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error Creating User")
        return new_user

    def create_superuser(self, db: Session, *, obj_in: UserCreate) -> User:
        return self.create(db, obj_in=obj_in, role_id=1)

    def create_admin(self, db: Session, *, obj_in: UserCreate) -> User:
        return self.create(db, obj_in=obj_in, role_id=2)

    def create_lecturer(self, db: Session, *, obj_in: UserCreate) -> User:
        return self.create(db, obj_in=obj_in, role_id=3)

    def create_student(self, db: Session, *, obj_in: UserCreate) -> User:
        return self.create(db, obj_in=obj_in, role_id=4)

    def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        if isinstance(db_obj, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
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
