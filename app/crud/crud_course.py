from app.crud.base import CRUDBase
from app.models.domains import Course
from app.models.schemas.course import CourseCreate, CourseUpdate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    pass


course = CRUDCourse(Course)
