from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings

router = APIRouter()


@router.get("/", response_model=List[schemas.Schedule], dependencies=[Depends(deps.get_current_active_user)])
def get_list_schedules(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 20):
    list_data = crud.schedule.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.Schedule, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_admin)])
def create_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(session.get_db)):
    return crud.schedule.create(db=db, obj_in=schedule)


@router.get("/{schedule_id}", response_model=schemas.Schedule, dependencies=[Depends(deps.get_current_active_user)])
def get_schedule(schedule_id: int, db: Session = Depends(session.get_db)):
    data = crud.schedule.get(db, schedule_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return data


@router.put('/{schedule_id}', response_model=schemas.Schedule, dependencies=[Depends(deps.get_current_admin)])
def update_schedule(schedule_id: int, schedule: schemas.ScheduleUpdate, db: Session = Depends(session.get_db)):
    db_obj = crud.schedule.get(db, schedule_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return crud.schedule.update(db=db, db_obj=db_obj, obj_in=schedule)


@router.delete('/{schedule_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(deps.get_current_admin)])
def delete_schedule(schedule_id: int, db: Session = Depends(session.get_db)):
    db_obj = crud.schedule.get(db, schedule_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=strings.ERROR_DATA_ID_NOT_EXIST.format(schedule_id))
    return crud.schedule.delete(db=db, id=schedule_id)
