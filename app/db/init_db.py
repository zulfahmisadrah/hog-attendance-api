import json
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import crud_user, crud_role, crud_faculty, crud_department
from app.models.schemas import UserCreate, RoleCreate, FacultyCreate, DepartmentCreate


def init_db(db: Session) -> None:

    json_file_role = open(settings.INITIAL_DATA_FOLDER + "role.json")
    for data_dict in json.load(json_file_role):
        data = crud_role.role.get(db, id=data_dict.get("id"))
        if not data:
            obj_in = RoleCreate(**data_dict)
            crud_role.role.create(db, obj_in=obj_in)

    user = crud_user.user.get_by_username(db, username=settings.FIRST_SUPERUSER_USERNAME)
    if not user:
        user_in = UserCreate(
            name=settings.FIRST_SUPERUSER_NAME,
            username=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
        )
        user = crud_user.user.create_superuser(db, obj_in=user_in)

    json_file_faculty = open(settings.INITIAL_DATA_FOLDER + "faculty.json")
    for data_dict in json.load(json_file_faculty):
        data = crud_faculty.faculty.get(db, id=data_dict.get("id"))
        if not data:
            obj_in = FacultyCreate(**data_dict)
            crud_faculty.faculty.create(db, obj_in=obj_in)

    json_file_department = open(settings.INITIAL_DATA_FOLDER + "department.json")
    for data_dict in json.load(json_file_department):
        data = crud_department.department.get(db, id=data_dict.get("id"))
        if not data:
            obj_in = DepartmentCreate(**data_dict)
            crud_department.department.create(db, obj_in=obj_in)
