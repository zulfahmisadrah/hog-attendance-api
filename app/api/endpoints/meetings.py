from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.models import domains, schemas
from app.api import deps
from app.db import session
from app.resources import strings

router = APIRouter()


@router.get("/", response_model=List[schemas.Meeting], dependencies=[Depends(deps.get_current_active_user)])
def get_list_meetings(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 20):
    list_data = crud.meeting.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.Meeting, status_code=status.HTTP_201_CREATED, dependencies=[Depends(deps.get_current_admin)])
def create_meeting(meeting: schemas.MeetingCreate, db: Session = Depends(session.get_db)):
    return crud.meeting.create(db=db, obj_in=meeting)


@router.get("/{meeting_id}", response_model=schemas.Meeting, dependencies=[Depends(deps.get_current_active_user)])
def get_meeting(meeting_id: int, db: Session = Depends(session.get_db)):
    data = crud.meeting.get(db, meeting_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return data


@router.put('/{meeting_id}', response_model=schemas.Meeting, dependencies=[Depends(deps.get_current_admin)])
def update_meeting(meeting_id: int, meeting: schemas.MeetingUpdate, db: Session = Depends(session.get_db)):
    db_obj = crud.meeting.get(db, meeting_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return crud.meeting.update(db=db, db_obj=db_obj, obj_in=meeting)


@router.delete('/{meeting_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(deps.get_current_admin)])
def delete_meeting(meeting_id: int, db: Session = Depends(session.get_db)):
    db_obj = crud.meeting.get(db, meeting_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_ID_NOT_EXIST.format(meeting_id))
    return crud.meeting.delete(db=db, id=meeting_id)

