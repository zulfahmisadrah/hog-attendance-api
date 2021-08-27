from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings

router = APIRouter()


@router.get("/", response_model=List[schemas.Student], dependencies=[Depends(deps.get_current_active_user)])
def get_list_students(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 20):
    list_data = crud.student.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.Student, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_admin)])
def create_student(student: schemas.StudentCreate, db: Session = Depends(session.get_db)):
    user = crud.user.get_by_username(db, username=student.user.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    return crud.student.create(db=db, obj_in=student)


@router.get("/{student_id}", response_model=schemas.Student, dependencies=[Depends(deps.get_current_active_user)])
def get_student(student_id: int, db: Session = Depends(session.get_db)):
    data = crud.student.get(db, student_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return data


@router.put('/{student_id}', response_model=schemas.Student, dependencies=[Depends(deps.get_current_admin)])
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
