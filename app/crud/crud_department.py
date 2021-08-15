from app.crud.base import CRUDBase
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentBase


class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentBase]):
    pass


department = CRUDDepartment(Department)
