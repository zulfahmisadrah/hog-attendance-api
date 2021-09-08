from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings

router = APIRouter()


@router.get("/", response_model=List[schemas.Lecturer], dependencies=[Depends(deps.get_current_active_user)])
def get_list_lecturers(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 20):
    list_data = crud.lecturer.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_admin)])
def create_lecturer(user_in: schemas.UserLecturerCreate, db: Session = Depends(deps.get_db)):
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    return crud.lecturer.create(db, obj_in=user_in)


@router.get("/{lecturer_id}", response_model=schemas.Lecturer, dependencies=[Depends(deps.get_current_active_user)])
def get_lecturer(lecturer_id: int, db: Session = Depends(session.get_db)):
    data = crud.lecturer.get(db, lecturer_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return data


@router.put('/{lecturer_id}', response_model=schemas.Lecturer, dependencies=[Depends(deps.get_current_admin)])
def update_lecturer(lecturer_id: int, lecturer: schemas.LecturerUpdate, db: Session = Depends(session.get_db)):
    db_obj = crud.lecturer.get(db, lecturer_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return crud.lecturer.update(db=db, db_obj=db_obj, obj_in=lecturer)


@router.delete('/{lecturer_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(deps.get_current_admin)])
def delete_lecturer(lecturer_id: int, db: Session = Depends(session.get_db)):
    db_obj = crud.lecturer.get(db, lecturer_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=strings.ERROR_DATA_ID_NOT_EXIST.format(lecturer_id))
    return crud.lecturer.delete(db=db, id=lecturer_id)
