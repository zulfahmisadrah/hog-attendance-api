from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import session
from app.courses import crud, schemas


router = APIRouter(
    prefix="/api/faculties",
    tags=["faculties"],

)


@router.get("/", response_model=List[schemas.Faculty])
def index(offset: int = 0, limit: int = 10, db: Session = Depends(session.get_db)):
    faculties = crud.get_faculties(db, offset=offset, limit=limit)
    return faculties


@router.get("/{faculty_id}/", response_model=schemas.Faculty)
def show(faculty_id: int, db: Session = Depends(session.get_db)):
    faculty = crud.get_faculty(db, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Data not found")
    return faculty


@router.post("/", response_model=schemas.Faculty, status_code=201)
def create(faculty: schemas.FacultyCreate, db: Session = Depends(session.get_db)):
    return crud.create_faculty(db=db, faculty=faculty)


@router.put('/{faculty_id}/')
def update(faculty_id: int, faculty: schemas.FacultyCreate, db: Session = Depends(session.get_db)):
    return crud.update_faculty(db=db, faculty_id=faculty_id, faculty=faculty)


@router.delete('/{faculty_id}/', status_code=204)
def destroy(faculty_id: int, db: Session = Depends(session.get_db)):
    return crud.delete_faculty(db=db, faculty_id=faculty_id)


@router.get("/{faculty_id}/departments/", response_model=schemas.FacultyDepartments)
def get_departments(faculty_id: int, db: Session = Depends(session.get_db)):
    faculty = crud.get_faculty(db, faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Data not found")
    return faculty
