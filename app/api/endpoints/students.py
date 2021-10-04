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


@router.get("/", response_model=List[schemas.StudentUser], dependencies=[Depends(deps.get_current_active_user)])
def get_list_students(
        department_id: Optional[int] = Query(None),
        keyword: Optional[str] = Query(None, min_length=3),
        offset: int = 0,
        limit: int = 20,
        db: Session = Depends(session.get_db)
):
    if department_id:
        if keyword:
            list_data = crud.student.get_by_department_id_and_username_or_name(db, department_id=department_id,
                                                                               keyword=keyword, offset=offset,
                                                                               limit=limit)
        else:
            list_data = crud.student.get_by_department_id(db, department_id=department_id)
    else:
        if keyword:
            list_data = crud.student.get_by_username_or_name(db, keyword=keyword, offset=offset, limit=limit)
        else:
            list_data = crud.student.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_admin)])
def create_student(student: schemas.UserStudentCreate, db: Session = Depends(deps.get_db)):
    user = crud.user.get_by_username(db, username=student.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    return crud.student.create(db, obj_in=student)


@router.get("/{student_id}", response_model=schemas.StudentUserSimple,
            dependencies=[Depends(deps.get_current_active_user)])
def get_student(student_id: int, db: Session = Depends(session.get_db)):
    student = crud.student.get(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_STUDENT, student_id)
        )
    return student


@router.put('/{student_id}', response_model=schemas.StudentUserSimple, dependencies=[Depends(deps.get_current_admin)])
def update_student(student_id: int, student: schemas.StudentUpdate, db: Session = Depends(session.get_db)):
    db_obj = crud.student.get(db, student_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return crud.student.update(db=db, db_obj=db_obj, obj_in=student)


@router.delete('/{student_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(deps.get_current_admin)])
def delete_student(student_id: int, db: Session = Depends(session.get_db)):
    db_obj = crud.student.get(db, student_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=strings.ERROR_DATA_ID_NOT_EXIST.format(student_id))
    return crud.student.delete(db=db, id=student_id)


@router.get("/{student_id}/courses", response_model=schemas.StudentCourses,
            dependencies=[Depends(deps.get_current_active_user)])
def get_student_courses(student_id: int, semester_id: int = 0, db: Session = Depends(session.get_db)):
    student = get_student(student_id, db)
    if semester_id == 0:
        semester = crud.semester.get_active_semester(db)
    else:
        semester = get_semester(semester_id, db)
    data = crud.student.get_student_courses(db, student_id=student_id, semester_id=semester_id)
    list_courses = []
    for student_course in data:
        course = schemas.Course.from_orm(student_course.course)
        list_courses.append(course)
    student_courses = schemas.StudentCourses(semester=semester, student=student, courses=list_courses)
    return student_courses
