from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings
from app.api.endpoints.semesters import get_semester

router = APIRouter()


@router.get("/", response_model=List[schemas.Course], dependencies=[Depends(deps.get_current_active_user)])
def get_list_courses(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 20):
    list_data = crud.course.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.Course, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_admin)])
def create_course(course: schemas.CourseCreate, db: Session = Depends(session.get_db)):
    return crud.course.create(db=db, obj_in=course)


@router.get("/{course_id}", response_model=schemas.Course, dependencies=[Depends(deps.get_current_active_user)])
def get_course(course_id: int, db: Session = Depends(session.get_db)):
    course = crud.course.get(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_COURSE, course_id)
        )
    return course


@router.put('/{course_id}', response_model=schemas.Course, dependencies=[Depends(deps.get_current_admin)])
def update_course(course_id: int, course: schemas.CourseUpdate, db: Session = Depends(session.get_db)):
    db_obj = crud.course.get(db, course_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return crud.course.update(db=db, db_obj=db_obj, obj_in=course)


@router.delete('/{course_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(deps.get_current_admin)])
def delete_course(course_id: int, db: Session = Depends(session.get_db)):
    db_obj = crud.course.get(db, course_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=strings.ERROR_DATA_ID_NOT_EXIST.format(course_id))
    return crud.course.delete(db=db, id=course_id)


@router.get("/{course_id}/lecturers", response_model=List[schemas.LecturerUserSimple],
            dependencies=[Depends(deps.get_current_active_user)])
def get_course_lecturers(course_id: int, semester_id: Optional[int] = None, db: Session = Depends(session.get_db)):
    get_course(course_id, db)
    if semester_id:
        semester = get_semester(semester_id, db)
    else:
        semester = crud.semester.get_active_semester(db)
    return crud.course.get_course_lecturers(db, course_id=course_id, semester_id=semester.id)


@router.get("/{course_id}/students", response_model=List[schemas.StudentUserSimple],
            dependencies=[Depends(deps.get_current_active_user)])
def get_course_students(course_id: int, semester_id: Optional[int] = None, db: Session = Depends(session.get_db)):
    get_course(course_id, db)
    if semester_id:
        semester = get_semester(semester_id, db)
    else:
        semester = crud.semester.get_active_semester(db)
    return crud.course.get_course_students(db, course_id=course_id, semester_id=semester.id)


@router.post("/{course_id}/lecturers", response_model=List[schemas.StudentUserSimple],
             dependencies=[Depends(deps.get_current_active_user)])
def add_course_lecturers(
        course_id: int,
        obj_in: schemas.CourseLecturersUpdate,
        db: Session = Depends(session.get_db),
):
    get_course(course_id, db)
    return crud.course.add_course_lecturers(db, course_id=course_id, obj_in=obj_in)


@router.post("/{course_id}/students", response_model=List[schemas.StudentUserSimple],
             dependencies=[Depends(deps.get_current_active_user)])
def add_course_students(
        course_id: int,
        obj_in: schemas.CourseStudentsUpdate,
        db: Session = Depends(session.get_db),
):
    get_course(course_id, db)
    return crud.course.add_course_students(db, course_id=course_id, obj_in=obj_in)


@router.delete("/{course_id}/lecturers", response_model=List[schemas.LecturerUserSimple], dependencies=[Depends(deps.get_current_active_user)])
def remove_course_lecturers(
        course_id: int,
        obj_in: schemas.CourseLecturersUpdate,
        db: Session = Depends(session.get_db),
):
    get_course(course_id, db)
    return crud.course.delete_course_lecturers(db, course_id=course_id, obj_in=obj_in)


@router.delete("/{course_id}/students", response_model=List[schemas.StudentUserSimple],
               dependencies=[Depends(deps.get_current_active_user)])
def remove_course_students(
        course_id: int,
        obj_in: schemas.CourseStudentsUpdate,
        db: Session = Depends(session.get_db),
):
    get_course(course_id, db)
    return crud.course.delete_course_students(db, course_id=course_id, obj_in=obj_in)
