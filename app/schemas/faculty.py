from typing import Optional, List

from fastapi_permissions import Allow, Authenticated
from pydantic import BaseModel

from app.schemas.department import Department


class FacultyBase(BaseModel):
    name: str
    code: str

    def __acl__(self):
        return [
            (Allow, Authenticated, "read"),
            (Allow, "role:admin", ("create", "update", "delete")),
        ]


class FacultyCreate(FacultyBase):
    pass


class FacultyUpdate(FacultyBase):
    name: Optional[str] = None
    code: Optional[str] = None


class Faculty(FacultyBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class FacultyDepartments(FacultyBase):
    id: int
    departments: List[Department] = []

    class Config:
        orm_mode = True
