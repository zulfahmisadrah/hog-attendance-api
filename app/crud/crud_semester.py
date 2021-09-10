from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.domains import Semester
from app.models.schemas.semester import SemesterCreate, SemesterUpdate


class CRUDSemester(CRUDBase[Semester, SemesterCreate, SemesterUpdate]):
    def get_active_semester(self, db: Session):
        return db.query(Semester).filter(Semester.is_active == 1).first()


semester = CRUDSemester(Semester)
