from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models import schemas
from app.resources.enums import DatasetType
from app.utils.file_helper import get_avatar_file, get_user_dataset_file, get_result_file, get_list_files, \
    get_user_datasets_directory, get_user_dataset_raw_file, get_meeting_results_directory

router = APIRouter()


@router.get("/avatar/{file_name}")
def get_avatar(file_name: str):
    if file_name == "null" or file_name == "undefined":
        avatar = get_avatar_file("null.jpg")
    else:
        avatar = get_avatar_file(file_name)
    return FileResponse(avatar)


@router.get("/dataset/sample/{username}")
def get_dataset_sample(username: str):
    datasets = get_list_files(get_user_datasets_directory(DatasetType.TRAINING, username))
    if datasets:
        sample = get_user_dataset_file(DatasetType.TRAINING, username, datasets[0])
    else:
        sample = get_avatar_file("null.jpg")
    return FileResponse(sample)


@router.get("/dataset/{dataset_type}/{username}/{file_name}")
def get_dataset(dataset_type: DatasetType, username: str, file_name: str):
    dataset = get_user_dataset_file(dataset_type, username, file_name)
    return FileResponse(dataset)


@router.get("/dataset-raw/{dataset_type}/{username}/{file_name}")
def get_raw_dataset(dataset_type: DatasetType, username: str, file_name: str):
    dataset = get_user_dataset_raw_file(dataset_type, username, file_name)
    return FileResponse(dataset)


@router.get("/result/{meeting_id}/{file_name}")
def get_result(meeting_id: int, file_name: str,
               current_semester: schemas.Semester = Depends(deps.get_active_semester),
               db: Session = Depends(deps.get_db)):
    meeting = crud.meeting.get(db, meeting_id)
    result = get_result_file(current_semester.code, meeting.course.code, meeting_id, file_name)
    return FileResponse(result)
