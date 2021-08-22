from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.domains import Department
from app.models.schemas.department import DepartmentCreate, DepartmentUpdate


class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentUpdate]):
    def get_by_faculty_id(self, db: Session, faculty_id: int) -> Optional[Department]:
        return db.query(Department).filter(Department.faculty_id == faculty_id).all()


department = CRUDDepartment(Department)
