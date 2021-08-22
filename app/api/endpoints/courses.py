from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings

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
    data = crud.course.get(db, course_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return data


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
