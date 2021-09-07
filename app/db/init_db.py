from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.core.config import settings
from app.db.db_seeder import DBSeeder
from app.resources.enums import RoleEnum


def init_db(db: Session) -> None:
    DBSeeder(db, crud.role, schemas.RoleCreate).load_from_json("role.json")

    user = crud.user.get_by_username(db, username=settings.FIRST_SUPERUSER_USERNAME)
    if not user:
        user_in = schemas.UserCreate(
            name=settings.FIRST_SUPERUSER_NAME,
            username=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            roles=[{"code": RoleEnum.SUPER_USER.value}]
        )
        crud.user.create(db, obj_in=user_in)

    DBSeeder(db, crud.user, schemas.UserCreate).load_from_json("user.json")
    DBSeeder(db, crud.lecturer, schemas.LecturerCreate).load_from_json("lecturer.json")
    DBSeeder(db, crud.student, schemas.StudentCreate).load_from_json("student.json")
    DBSeeder(db, crud.faculty, schemas.FacultyCreate).load_from_json("faculty.json")
    DBSeeder(db, crud.department, schemas.DepartmentCreate).load_from_json("department.json")
