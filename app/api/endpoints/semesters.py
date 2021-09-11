from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings

router = APIRouter()


@router.get("/", response_model=List[schemas.Semester], dependencies=[Depends(deps.get_current_active_user)])
def get_list_semesters(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 20):
    list_data = crud.semester.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.Semester, status_code=201, dependencies=[Depends(deps.get_current_admin)])
def create_semester(semester: schemas.SemesterCreate, db: Session = Depends(session.get_db)):
    return crud.semester.create(db=db, obj_in=semester)


@router.get("/{semester_id}", response_model=schemas.Semester, dependencies=[Depends(deps.get_current_active_user)])
def get_semester(semester_id: int, db: Session = Depends(session.get_db)):
    semester = crud.semester.get(db, semester_id)
    if not semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_SEMESTER, semester_id)
        )
    return semester


@router.put('/{semester_id}', response_model=schemas.Semester, dependencies=[Depends(deps.get_current_admin)])
def update_semester(semester_id: int, semester: schemas.SemesterUpdate, db: Session = Depends(session.get_db)):
    db_obj = crud.semester.get(db, semester_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail=strings.ERROR_DATA_NOT_FOUND)
    return crud.semester.update(db=db, db_obj=db_obj, obj_in=semester)


@router.delete('/{semester_id}', status_code=204, dependencies=[Depends(deps.get_current_admin)])
def delete_semester(semester_id: int, db: Session = Depends(session.get_db)):
    db_obj = crud.semester.get(db, semester_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail=strings.ERROR_DATA_ID_NOT_EXIST.format(semester_id))
    return crud.semester.delete(db=db, id=semester_id)
