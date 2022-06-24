from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.db import session
from app.models import schemas
from app.resources import strings
from app.resources.enums import MeetingType

router = APIRouter()


@router.get("/", response_model=List[schemas.Meeting], dependencies=[Depends(deps.get_current_active_user)])
def get_list_meetings(db: Session = Depends(session.get_db), offset: int = 0, limit: int = 20):
    list_data = crud.meeting.get_list_meeting(db, offset=offset, limit=limit)
    return list_data


@router.post("/", response_model=schemas.Meeting, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_admin)])
def create_meeting(meeting: schemas.MeetingCreate, db: Session = Depends(session.get_db)):
    if not meeting.name:
        course = crud.course.get(db, meeting.course_id)
        meeting.name = f"{course.name} #{meeting.number}" if meeting.number else course.name
    return crud.meeting.create(db=db, obj_in=meeting)


@router.get("/me", response_model=List[schemas.Meeting])
def get_my_meetings(
        db: Session = Depends(session.get_db),
        current_semester: schemas.Semester = Depends(deps.get_active_semester),
        current_user: Union[schemas.UserLecturer, schemas.UserStudent] = Depends(deps.get_current_active_user)
):
    if current_user.student:
        student_id = current_user.student.id
        user_courses = crud.student.get_student_courses(db, student_id=student_id, semester_id=current_semester.id)
    else:
        lecturer_id = current_user.lecturer.id
        user_courses = crud.lecturer.get_lecturer_courses(db, lecturer_id=lecturer_id, semester_id=current_semester.id)
    list_meetings = []
    for user_course in user_courses:
        meetings: List[schemas.Meeting] = user_course.course.meetings
        crud.meeting.update_meetings_status(db, meetings)
        list_meetings.extend(meetings)
    return list_meetings


@router.get("/me/{meeting_type}", response_model=List[schemas.Meeting])
def get_my_meetings_today(
        meeting_type: str,
        db: Session = Depends(session.get_db),
        offset: int = 0, limit: int = 10,
        current_semester: schemas.Semester = Depends(deps.get_active_semester),
        current_user: Union[schemas.UserLecturer, schemas.UserStudent] = Depends(deps.get_current_active_user)
):
    if current_user.student:
        student_id = current_user.student.id
        user_courses = crud.student.get_student_courses(db, student_id=student_id, semester_id=current_semester.id)
    else:
        lecturer_id = current_user.lecturer.id
        user_courses = crud.lecturer.get_lecturer_courses(db, lecturer_id=lecturer_id, semester_id=current_semester.id)

    if meeting_type == MeetingType.NEAREST:
        get_meetings = crud.meeting.get_meetings_nearest
    elif meeting_type == MeetingType.TODAY:
        get_meetings = crud.meeting.get_meetings_today
    elif meeting_type == MeetingType.UPCOMING:
        get_meetings = crud.meeting.get_meetings_upcoming
    elif meeting_type == MeetingType.FINISHED:
        get_meetings = crud.meeting.get_meetings_finished
    else:
        get_meetings = crud.meeting.get_meetings_by_course_id
    list_meetings = []
    for user_course in user_courses:
        meetings = get_meetings(db, course_id=user_course.course_id, offset=offset, limit=limit)
        crud.meeting.update_meetings_status(db, meetings)
        list_meetings.extend(meetings)
    return list_meetings


@router.get("/{meeting_id}", response_model=schemas.Meeting, dependencies=[Depends(deps.get_current_active_user)])
def get_meeting(meeting_id: int, db: Session = Depends(session.get_db)):
    data = crud.meeting.get(db, meeting_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.ERROR_DATA_NOT_FOUND)
    return data


@router.put('/{meeting_id}', response_model=schemas.Meeting)
def update_meeting(
        meeting_id: int,
        meeting: schemas.MeetingUpdate,
        db: Session = Depends(session.get_db),
        current_user: schemas.UserLecturer = Depends(deps.get_current_active_user)
):
    db_obj = crud.meeting.get(db, meeting_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=strings.ERROR_MODEL_ID_NOT_EXIST.format(strings.MODEL_MEETING))
    if crud.user.is_admin(current_user) or crud.user.is_lecturer(current_user):
        if not meeting.name:
            course = crud.course.get(db, meeting.course_id)
            meeting.name = f"{course.name} #{meeting.number}"
        return crud.meeting.update(db=db, db_obj=db_obj, obj_in=meeting)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=strings.USER_FORBIDDEN)


@router.delete('/{meeting_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(deps.get_current_admin)])
def delete_meeting(meeting_id: int, db: Session = Depends(session.get_db)):
    db_obj = crud.meeting.get(db, meeting_id)
    if db_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=strings.ERROR_DATA_ID_NOT_EXIST.format(meeting_id))
    return crud.meeting.delete(db=db, id=meeting_id)


@router.get("/{meeting_id}/attendances",
            response_model=List[schemas.Attendance],
            dependencies=[Depends(deps.get_current_active_user)])
def get_meeting_attendances(meeting_id: int, db: Session = Depends(session.get_db)):
    get_meeting(meeting_id, db)
    data = crud.meeting.get_meeting_attendances(db, meeting_id=meeting_id)
    return data


@router.get("/course/{course_id}", response_model=List[schemas.Meeting],
            dependencies=[Depends(deps.get_current_admin)])
def get_course_meetings(course_id: int, db: Session = Depends(session.get_db)):
    return crud.meeting.get_meetings_by_course_id(db, course_id=course_id)
