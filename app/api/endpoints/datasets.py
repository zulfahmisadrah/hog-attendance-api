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
    result = datasets.create_models(semester.code, course.code, validate=True, save_preprocessing=True,
                                    grid_search=False)
    return result


@router.post("/recognize", dependencies=[Depends(deps.get_current_active_user)])
def recognize(course_id: int = Form(...), file: Union[bytes, UploadFile] = File(...),
              semester: schemas.Semester = Depends(deps.get_active_semester), db: Session = Depends(session.get_db)):
    course = crud.course.get(db, course_id)
    results = datasets.recognize_face(file, semester.code, course.code)
    return results


@router.post("/capture", dependencies=[Depends(deps.get_current_admin)])
async def capture(username: str = Form(...), file: Union[bytes, UploadFile] = File(...)):
    result = await datasets.create_dataset(file, username)
    return result


@router.post("/detect_from_raw", dependencies=[Depends(deps.get_current_admin)])
def detect_from_raw(username: str = Form(...)):
    result = datasets.generate_datasets_from_folder(username)
    # result = datasets.generate_datasets_from_folder_all()
    return result


@router.get("/{username}", dependencies=[Depends(deps.get_current_admin)])
def get_list_user_datasets(username: str):
    list_datasets = datasets.get_user_datasets(username)
    return list_datasets


@router.delete('/{username}/{file_name}', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(deps.get_current_admin)])
def delete_dataset(username: str, file_name: str):
    return crud_dataset.delete_user_dataset(username, file_name)
