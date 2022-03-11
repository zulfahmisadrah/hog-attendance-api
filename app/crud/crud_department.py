from typing import Optional, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.domains import Department
from app.models.schemas.department import DepartmentCreate, DepartmentUpdate


class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentUpdate]):
    def get_by_faculty_id(self, db: Session, faculty_id: int) -> List[Department]:
        return db.query(Department).filter(Department.faculty_id == faculty_id).all()

    def get_by_username_parsing(self, db: Session, username: str) -> Optional[Department]:
        code = username[:3] if len(username) > 3 else ""
        return db.query(Department).filter(Department.code == code).first()


department = CRUDDepartment(Department)
