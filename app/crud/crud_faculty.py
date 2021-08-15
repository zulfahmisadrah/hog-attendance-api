from app.crud.base import CRUDBase
from app.models.domains import Faculty
from app.models.schemas.faculty import FacultyCreate, FacultyUpdate


class CRUDFaculty(CRUDBase[Faculty, FacultyCreate, FacultyUpdate]):
    pass


faculty = CRUDFaculty(Faculty)
