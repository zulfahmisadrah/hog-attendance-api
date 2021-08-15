from app.crud.base import CRUDBase
from app.models.domains import Department
from app.models.schemas.department import DepartmentCreate, DepartmentBase


class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentBase]):
    pass


department = CRUDDepartment(Department)
