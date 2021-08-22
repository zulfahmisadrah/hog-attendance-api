from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings

router = APIRouter()


@router.get("/", response_model=List[schemas.Faculty], dependencies=[Depends(deps.get_current_active_user)])
def get_list_faculties(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 20):
    list_data = crud.faculty.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.Faculty, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_admin)])
def create_faculty(faculty: schemas.FacultyCreate, db: Session = Depends(session.get_db)):
    return crud.faculty.create(db=db, obj_in=faculty)


@router.get("/{faculty_id}", response_model=schemas.Faculty, dependencies=[Depends(deps.get_current_active_user)])
def get_faculty(faculty_id: int, db: Session = Depends(session.get_db)):
    data = crud.faculty.get(db, faculty_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return data


@router.put('/{faculty_id}', response_model=schemas.Faculty, dependencies=[Depends(deps.get_current_admin)])
def update_faculty(faculty_id: int, faculty: schemas.FacultyUpdate, db: Session = Depends(session.get_db)):
    db_obj = crud.faculty.get(db, faculty_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return crud.faculty.update(db=db, db_obj=db_obj, obj_in=faculty)


@router.delete('/{faculty_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(deps.get_current_admin)])
def delete_faculty(faculty_id: int, db: Session = Depends(session.get_db)):
    db_obj = crud.faculty.get(db, faculty_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=strings.ERROR_DATA_ID_NOT_EXIST.format(faculty_id))
    return crud.faculty.delete(db=db, id=faculty_id)


@router.get("/{faculty_id}/departments", response_model=schemas.FacultyDepartments)
def get_with_departments(faculty_id: int, db: Session = Depends(session.get_db)):
    faculty = crud.faculty.get(db, faculty_id)
    if not faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return faculty
