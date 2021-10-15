from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings

router = APIRouter()


@router.get("/", response_model=List[schemas.Attendance], dependencies=[Depends(deps.get_current_active_user)])
def get_list_attendances(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 20):
    list_data = crud.attendance.get_list(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.Attendance, status_code=201, dependencies=[Depends(deps.get_current_admin)])
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(session.get_db)):
    return crud.attendance.create(db=db, obj_in=attendance)


@router.get("/me", response_model=List[schemas.Attendance])
def get_my_attendances(
        db: Session = Depends(session.get_db),
        current_user: schemas.UserStudent = Depends(deps.get_current_active_user)
):
    return crud.attendance.get_attendances_by_student_id(db, student_id=current_user.student.id)


@router.get("/{attendance_id}", response_model=schemas.Attendance, dependencies=[Depends(deps.get_current_active_user)])
def get_attendance(attendance_id: int, db: Session = Depends(session.get_db)):
    attendance = crud.attendance.get(db, attendance_id)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_SEMESTER, attendance_id)
        )
    return attendance


@router.put('/{attendance_id}', response_model=schemas.Attendance, dependencies=[Depends(deps.get_current_active_user)])
def update_attendance(attendance_id: int, attendance: schemas.AttendanceUpdate, db: Session = Depends(session.get_db)):
    db_obj = crud.attendance.get(db, attendance_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail=strings.ERROR_DATA_NOT_FOUND)
    return crud.attendance.update(db=db, db_obj=db_obj, obj_in=attendance)


@router.delete('/{attendance_id}', status_code=204, dependencies=[Depends(deps.get_current_admin)])
def delete_attendance(attendance_id: int, db: Session = Depends(session.get_db)):
    db_obj = crud.attendance.get(db, attendance_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail=strings.ERROR_DATA_ID_NOT_EXIST.format(attendance_id))
    return crud.attendance.delete(db=db, id=attendance_id)


# @router.put('/batch', response_model=List[schemas.Attendance], dependencies=[Depends(deps.get_current_admin)])
# def update_attendance(attendances: List[schemas.Attendance], db: Session = Depends(session.get_db)):
#     db_obj = crud.attendance.get(db, attendance_id)
#     if db_obj is None:
#         raise HTTPException(status_code=404, detail=strings.ERROR_DATA_NOT_FOUND)
#     return crud.attendance.update(db=db, db_obj=db_obj, obj_in=attendance)