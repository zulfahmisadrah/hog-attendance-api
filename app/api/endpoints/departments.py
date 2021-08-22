from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings

router = APIRouter()


@router.get("/", response_model=List[schemas.Department], dependencies=[Depends(deps.get_current_active_user)])
def get_list_departments(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 20):
    list_data = crud.department.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.Department, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_admin)])
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(session.get_db)):
    return crud.department.create(db=db, obj_in=department)


@router.get("/faculty/{faculty_id}", response_model=List[schemas.Department],
            dependencies=[Depends(deps.get_current_active_user)])
def get_departments_of_faculty(faculty_id: int, db: Session = Depends(session.get_db)):
    data = crud.department.get_by_faculty_id(db, faculty_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return data


@router.get("/{department_id}", response_model=schemas.Department, dependencies=[Depends(deps.get_current_active_user)])
def get_department(department_id: int, db: Session = Depends(session.get_db)):
    department = crud.department.get(db, department_id)
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return department


@router.put('/{department_id}', response_model=schemas.Department, dependencies=[Depends(deps.get_current_admin)])
def update_department(department_id: int, department: schemas.DepartmentUpdate, db: Session = Depends(session.get_db)):
    db_obj = crud.department.get(db, department_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return crud.department.update(db=db, db_obj=db_obj, obj_in=department)


@router.delete('/{department_id}', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(deps.get_current_admin)])
def delete_department(department_id: int, db: Session = Depends(session.get_db)):
    db_obj = crud.department.get(db, department_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=strings.ERROR_DATA_ID_NOT_EXIST.format(department_id))
    return crud.department.delete(db=db, id=department_id)


@router.get("/{department_id}/courses", response_model=schemas.DepartmentCourses,
            dependencies=[Depends(deps.get_current_active_user)])
def get_with_departments(department_id: int, db: Session = Depends(session.get_db)):
    department = crud.department.get(db, department_id)
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return department
