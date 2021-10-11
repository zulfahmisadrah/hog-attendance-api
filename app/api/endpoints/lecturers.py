from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings
from app.api.endpoints.semesters import get_semester

router = APIRouter()


@router.get("/", response_model=List[schemas.LecturerUser], dependencies=[Depends(deps.get_current_active_user)])
def get_list_lecturers(
        department_id: Optional[int] = Query(None),
        keyword: Optional[str] = Query(None, min_length=3),
        offset: int = 0,
        limit: int = 20,
        db: Session = Depends(session.get_db)
):
    if department_id:
        if keyword:
            list_data = crud.lecturer.get_by_department_id_and_username_or_name(db, department_id=department_id,
                                                                                keyword=keyword, offset=offset,
                                                                                limit=limit)
        else:
            list_data = crud.lecturer.get_by_department_id(db, department_id=department_id)
    else:
        if keyword:
            list_data = crud.lecturer.get_by_username_or_name(db, keyword=keyword, offset=offset, limit=limit)
        else:
            list_data = crud.lecturer.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_admin)])
def create_lecturer(user_in: schemas.UserLecturerCreate, db: Session = Depends(deps.get_db)):
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    return crud.lecturer.create(db, obj_in=user_in)


@router.get("/{lecturer_id}", response_model=schemas.LecturerUserSimple,
            dependencies=[Depends(deps.get_current_active_user)])
def get_lecturer(lecturer_id: int, db: Session = Depends(session.get_db)):
    lecturer = crud.lecturer.get(db, lecturer_id)
    if not lecturer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_LECTURER, lecturer_id)
        )
    return lecturer


@router.put('/{lecturer_id}', response_model=schemas.UserLecturer, dependencies=[Depends(deps.get_current_admin)])
def update_lecturer(lecturer_id: int, lecturer: schemas.UserUpdate, db: Session = Depends(session.get_db)):
    db_obj = get_lecturer(lecturer_id, db)
    return crud.lecturer.update(db=db, db_obj=db_obj.user, obj_in=lecturer)


@router.delete('/{lecturer_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(deps.get_current_admin)])
def delete_lecturer(lecturer_id: int, db: Session = Depends(session.get_db)):
    lecturer = get_lecturer(lecturer_id, db)
    return crud.lecturer.delete(db=db, db_obj=lecturer)


@router.get("/{lecturer_id}/courses", response_model=schemas.LecturerCourses,
            dependencies=[Depends(deps.get_current_active_user)])
def get_lecturer_courses(lecturer_id: int, semester_id: int = 0, db: Session = Depends(session.get_db)):
    lecturer = get_lecturer(lecturer_id, db)
    if semester_id == 0:
        semester = crud.semester.get_active_semester(db)
    else:
        semester = get_semester(semester_id, db)
    data = crud.lecturer.get_lecturer_courses(db, lecturer_id=lecturer_id, semester_id=semester_id)
    list_courses = []
    for lecturer_course in data:
        course = schemas.Course.from_orm(lecturer_course.course)
        list_courses.append(course)
    lecturer_courses = schemas.LecturerCourses(semester=semester, lecturer=lecturer, courses=list_courses)
    return lecturer_courses
