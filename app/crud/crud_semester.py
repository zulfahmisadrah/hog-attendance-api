from app.crud.base import CRUDBase
from app.models.domains import Semester
from app.models.schemas.semester import SemesterCreate, SemesterUpdate


class CRUDSemester(CRUDBase[Semester, SemesterCreate, SemesterUpdate]):
    pass


semester = CRUDSemester(Semester)
