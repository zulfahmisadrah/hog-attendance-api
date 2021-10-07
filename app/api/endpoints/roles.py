from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings

router = APIRouter()


@router.get("/", response_model=List[schemas.Role], dependencies=[Depends(deps.get_current_active_user)])
def get_list_roles(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 20):
    list_data = crud.role.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.Role, status_code=201, dependencies=[Depends(deps.get_current_admin)])
def create_role(role: schemas.RoleCreate, db: Session = Depends(session.get_db)):
    return crud.role.create(db=db, obj_in=role)


@router.get("/{role_id}", response_model=schemas.Role, dependencies=[Depends(deps.get_current_active_user)])
def get_role(role_id: int, db: Session = Depends(session.get_db)):
    role = crud.role.get(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_SEMESTER, role_id)
        )
    return role


@router.put('/{role_id}', response_model=schemas.Role, dependencies=[Depends(deps.get_current_admin)])
def update_role(role_id: int, role: schemas.RoleUpdate, db: Session = Depends(session.get_db)):
    db_obj = crud.role.get(db, role_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail=strings.ERROR_DATA_NOT_FOUND)
    return crud.role.update(db=db, db_obj=db_obj, obj_in=role)


@router.delete('/{role_id}', status_code=204, dependencies=[Depends(deps.get_current_admin)])
def delete_role(role_id: int, db: Session = Depends(session.get_db)):
    db_obj = crud.role.get(db, role_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail=strings.ERROR_DATA_ID_NOT_EXIST.format(role_id))
    return crud.role.delete(db=db, id=role_id)
