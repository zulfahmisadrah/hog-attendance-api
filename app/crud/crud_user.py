from typing import Optional, Union, Dict, Any

import aiofiles
from os import path
from fastapi import HTTPException, status, UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import crud_role
from app.crud.base import CRUDBase
from app.resources import strings
from app.resources.enums import RoleEnum
from app.models.domains import User, Student, Lecturer
from app.models.schemas import UserCreate, UserUpdate, UserStudentCreate, UserLecturerCreate, UserRolesCreate, \
    UserPasswordUpdate
from app.core.security import get_password_hash, verify_password
from app.utils.commons import get_current_datetime


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: Union[UserCreate, UserRolesCreate]) -> User:
        user_dict = jsonable_encoder(obj_in.copy(exclude={"roles"}))
        if user_dict["password"]:
            hashed_password = get_password_hash(user_dict["password"])
            user_dict["password"] = hashed_password
        try:
            new_user = User(**user_dict)
            if type(obj_in) is UserRolesCreate:
                list_roles = jsonable_encoder(obj_in.roles)
                for role_id in list_roles:
                    user_role = crud_role.role.get(db, id=role_id)
                    if user_role is not None:
                        new_user.roles.append(user_role)
                    else:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                            detail=strings.ROLE_INVALID)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
        except SQLAlchemyError as e:
            print(e.args)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=strings.ERROR_INTERNAL_SERVER_ERROR)
        return new_user

    def create_lecturer(self, db: Session, *, obj_in: UserLecturerCreate) -> User:
        new_user = self.create(db, obj_in=obj_in.copy(exclude={"lecturer"}))
        user_role = crud_role.role.get_by_code(db, code=RoleEnum.LECTURER.value)
        new_user.roles.append(user_role)
        lecturer_dict = jsonable_encoder(obj_in.lecturer)
        new_lecturer = Lecturer(user_id=new_user.id, **lecturer_dict)
        db.add(new_lecturer)
        db.commit()
        return new_user

    def create_student(self, db: Session, *, obj_in: UserStudentCreate) -> User:
        new_user = self.create(db, obj_in=obj_in.copy(exclude={"student"}))
        user_role = crud_role.role.get_by_code(db, code=RoleEnum.STUDENT.value)
        new_user.roles.append(user_role)
        student_dict = jsonable_encoder(obj_in.student)
        new_student = Student(user_id=new_user.id, **student_dict)
        db.add(new_student)
        db.commit()
        return new_user

    def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("lecturer"):
            lecturer_data = update_data.get("lecturer")
            db.query(Lecturer).filter_by(user_id=db_obj.id).update(lecturer_data)
        elif update_data.get("student"):
            student_data = update_data.get("student")
            db.query(Student).filter_by(user_id=db_obj.id).update(student_data)
        if update_data.get("password"):
            del update_data["password"]
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def update_password(self, db: Session, *, db_obj: User, obj_in: UserPasswordUpdate) -> User:
        hashed_password = get_password_hash(obj_in.new_password)
        db_obj.password = hashed_password
        db.query(User).filter_by(username=db_obj.username).update({User.password: hashed_password})
        db.commit()
        db.refresh(db_obj)
        return db_obj

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

    def is_lecturer(self, user: User):
        list_user_roles = [role_dict.code for role_dict in user.roles]
        return RoleEnum.LECTURER in list_user_roles

    async def upload_avatar(self, avatar: UploadFile, username: str) -> str:
        file_name = username + "_" + get_current_datetime() + ".jpg"
        file_path = path.join(settings.ASSETS_AVATAR_FOLDER, file_name)
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await avatar.read()
            await out_file.write(content)
        return file_name


user = CRUDUser(User)
