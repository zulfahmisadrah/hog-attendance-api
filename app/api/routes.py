from fastapi import APIRouter

from app.api.endpoints import auth, users, students, lecturers, faculties, departments, semesters, schedules, courses, meetings, datasets

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(lecturers.router, prefix="/lecturers", tags=["lecturers"])
api_router.include_router(faculties.router, prefix="/faculties", tags=["faculties"])
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(semesters.router, prefix="/semesters", tags=["semesters"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
