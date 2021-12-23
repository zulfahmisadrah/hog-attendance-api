from typing import Union

from fastapi import File, APIRouter, Depends, Form, status, UploadFile
from sqlalchemy.orm import Session

from app import crud
from app.crud import crud_dataset
from app.models import schemas
from app.api import deps
from app.db import session
from app.services import datasets

router = APIRouter()


@router.get("/", dependencies=[Depends(deps.get_current_admin)])
def get_list_datasets(db: Session = Depends(session.get_db)):
    list_datasets = crud_dataset.get_list_datasets(db)
    return list_datasets


@router.post("/train", dependencies=[Depends(deps.get_current_admin)])
def train(course_id: int = Form(...), semester: schemas.Semester = Depends(deps.get_active_semester),
          db: Session = Depends(session.get_db)):
    course = crud.course.get(db, course_id)
    file_path = datasets.create_models(semester.code, course.code, validate=True)
    return {
        "file_path": file_path
    }


@router.post("/recognize", dependencies=[Depends(deps.get_current_active_user)])
def recognize(course_id: int = Form(...), file: Union[bytes, UploadFile] = File(...),
              semester: schemas.Semester = Depends(deps.get_active_semester), db: Session = Depends(session.get_db)):
    course = crud.course.get(db, course_id)
    results = datasets.recognize_face(file, semester.code, course.code)
    # recognized_users = []
    # for result in results.get("predictions"):
    #     user = crud.user.get_by_username(db, username=result.get("label"))
    #     recognized_users.append(user)
    # print("RECOGNIZED USER", results.get("predictions"))

    # result, box = datasets.recognize_face(file, semester.code, course.code)
    return results


@router.post("/capture", dependencies=[Depends(deps.get_current_admin)])
async def capture(username: str = Form(...), file: Union[bytes, UploadFile] = File(...)):
    file_path = await datasets.save_user_image(file, username)
    return {
        "file_path": file_path
    }


@router.post("/detect_from_raw", dependencies=[Depends(deps.get_current_admin)])
def detect_from_raw(username: str = Form(...)):
    file_path = datasets.detect_faces_from_datasets_raw(username)
    # file_path = datasets.detect_faces_from_datasets_raw_all()
    return {
        "result": file_path
    }


@router.get("/{username}", dependencies=[Depends(deps.get_current_admin)])
def get_list_user_datasets(username: str):
    list_datasets = datasets.get_user_datasets(username)
    return list_datasets


@router.delete('/{username}/{file_name}', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(deps.get_current_admin)])
def delete_dataset(username: str, file_name: str):
    return crud_dataset.delete_user_dataset(username, file_name)
