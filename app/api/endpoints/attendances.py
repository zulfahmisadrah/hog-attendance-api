from typing import Union, List
from fastapi import File, APIRouter, Depends, Form, status, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings
from app.resources.enums import AttendanceStatus
from app.services import datasets

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


@router.post("/take_presence", dependencies=[Depends(deps.get_current_active_user)])
def take_presence(meeting_id: int = Form(...), validate: bool = Form(...), file: Union[bytes, UploadFile] = File(...),
              semester: schemas.Semester = Depends(deps.get_active_semester), db: Session = Depends(session.get_db)):
    meeting = crud.meeting.get(db, meeting_id)
    results = datasets.recognize_face(file, semester.code, meeting.course.code, save_preprocessing=True)
    for prediction in results['predictions']:
        student = crud.student.get_by_username(db, username=prediction['username'])
        attendance = crud.attendance.get_attendances_by_meeting_id_and_student_id(
            db,
            meeting_id=meeting_id,
            student_id=student.id
        )
        if validate:
            attendance_in = schemas.AttendanceUpdate(status_validate=AttendanceStatus.Hadir)
        else:
            attendance_in = schemas.AttendanceUpdate(status=AttendanceStatus.Hadir)
        crud.attendance.update(db, db_obj=attendance, obj_in=attendance_in)
    return results


@router.post("/reset_attendance_validate", dependencies=[Depends(deps.get_current_active_user)])
def reset_attendance_validate(meeting_id: int = Form(...), db: Session = Depends(session.get_db)):
    meeting = crud.meeting.get(db, meeting_id)
    crud.attendance.reset_attendance_validate(db, meeting_id=meeting.id)
    return "DONE"


@router.post("/apply_attendance_validate", dependencies=[Depends(deps.get_current_active_user)])
def apply_attendance_validate(meeting_id: int = Form(...), db: Session = Depends(session.get_db)):
    meeting = crud.meeting.get(db, meeting_id)
    attendances = crud.attendance.get_attendances_by_meeting_id(db, meeting_id=meeting.id)
    for attendance in attendances:
        attendance_in = schemas.AttendanceUpdate(status=attendance.status_validate)
        crud.attendance.update(db, db_obj=attendance, obj_in=attendance_in)
    return "DONE"


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


@router.get("/{meeting_id}/me", response_model=schemas.Attendance)
def get_my_meeting_attendance(
        meeting_id: int,
        db: Session = Depends(session.get_db),
        current_user: schemas.UserStudent = Depends(deps.get_current_active_user)
):
    return crud.attendance.get_attendances_by_meeting_id_and_student_id(db, meeting_id=meeting_id,
                                                                        student_id=current_user.student.id)
