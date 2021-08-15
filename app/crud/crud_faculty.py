from app.crud.base import CRUDBase
from app.models.faculty import Faculty
from app.schemas.faculty import FacultyCreate, FacultyUpdate


class CRUDFaculty(CRUDBase[Faculty, FacultyCreate, FacultyUpdate]):
    pass


faculty = CRUDFaculty(Faculty)
