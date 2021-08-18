from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.models import domains, schemas
from app.api import deps
from app.db import session

router = APIRouter()


@router.get("/", response_model=List[schemas.Faculty])
def index(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 10,
          current_user: domains.User = Depends(deps.get_current_active_user)):
    faculties = crud.faculty.get_list(db, offset=offset, limit=limit)
    return faculties


@router.post("/", response_model=schemas.Faculty, status_code=201)
def create(faculty: schemas.FacultyCreate, db: Session = Depends(session.get_db),
           current_user: domains.User = Depends(deps.get_current_admin)):
    return crud.faculty.create(db=db, obj_in=faculty)


@router.get("/{faculty_id}", response_model=schemas.Faculty)
def show(faculty_id: int, db: Session = Depends(session.get_db)):
    faculty = crud.faculty.get(db, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Data not found")
    return faculty


@router.put('/{faculty_id}')
def update(faculty_id: int, faculty: schemas.FacultyUpdate, db: Session = Depends(session.get_db)):
    db_obj = crud.faculty.get(db, faculty_id)
    return crud.faculty.update(db=db, db_obj=db_obj, obj_in=faculty)


@router.delete('/{faculty_id}', status_code=204)
def destroy(faculty_id: int, db: Session = Depends(session.get_db)):
    return crud.faculty.delete(db=db, id=faculty_id)


@router.get("/{faculty_id}/departments/", response_model=schemas.FacultyDepartments)
def get_departments(faculty_id: int, db: Session = Depends(session.get_db)):
    faculty = crud.faculty.get(db, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Data not found")
    return faculty
