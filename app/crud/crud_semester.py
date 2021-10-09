from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.domains import Semester
from app.models.domains.semester import SemesterType
from app.models.schemas.semester import SemesterCreate, SemesterUpdate


class CRUDSemester(CRUDBase[Semester, SemesterCreate, SemesterUpdate]):
    def get_active_semester(self, db: Session) -> Semester:
        return db.query(Semester).filter(Semester.is_active == 1).first()

    def activate_semester(self, db: Session, semester_id: int) -> None:
        current_active_semester = self.get_active_semester(db)
        db.query(Semester).filter(Semester.id == current_active_semester.id).update({Semester.is_active: 0})
        db.query(Semester).filter(Semester.id == semester_id).update({Semester.is_active: 1})
        db.commit()

    def get_latest_semester(self, db: Session) -> Semester:
        latest_year = db.query(func.max(Semester.year)).scalar_subquery()
        latest_year_semesters = db.query(Semester).filter(Semester.year == latest_year).all()
        latest_semester = latest_year_semesters[0]
        if len(latest_year_semesters) == 2:
            for latest_year_semester in latest_year_semesters:
                if latest_year_semester.type == SemesterType.GANJIL:
                    latest_semester = latest_year_semester
        return latest_semester


semester = CRUDSemester(Semester)
