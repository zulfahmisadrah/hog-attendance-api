from fastapi.logger import logger
from typing import Union, List

from fastapi import File, APIRouter, Depends, Form, status, UploadFile
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.db import session
from app.models import schemas
from app.services import datasets
from app.resources.enums import DatasetType

router = APIRouter()


@router.get("/", dependencies=[Depends(deps.get_current_admin)])
def get_list_datasets(db: Session = Depends(session.get_db)):
    list_datasets = datasets.get_list_datasets(db)
    return list_datasets


@router.get("/config", dependencies=[Depends(deps.get_current_admin)])
def get_datasets_config(db: Session = Depends(session.get_db)):
    face_recognition_method = crud.site_setting.use_facenet(db)
    with_masked_datasets = crud.site_setting.datasets_with_mask(db)
    result = {
        "face_recognition_method": face_recognition_method,
        "with_masked_datasets": with_masked_datasets
    }
    return result


@router.post("/train", dependencies=[Depends(deps.get_current_admin)])
def train(params: schemas.TrainingParams, semester: schemas.Semester = Depends(deps.get_active_semester),
          db: Session = Depends(session.get_db)):
    course = crud.course.get(db, params.course_id)
    result = datasets.create_models(db, semester.code, course.code, validate=params.validate_model,
                                    save_preprocessing=params.save_preprocessing, grid_search=params.deep_training)
    return result


@router.post("/recognize", dependencies=[Depends(deps.get_current_active_user)])
def recognize(course_id: int = Form(...), file: Union[bytes, UploadFile] = File(...),
              semester: schemas.Semester = Depends(deps.get_active_semester), db: Session = Depends(session.get_db)):
    course = crud.course.get(db, course_id)
    results = datasets.recognize_face(db, file, semester.code, course.code, meeting_id=0, save_preprocessing=True)
    return results


@router.post("/capture", dependencies=[Depends(deps.get_admin_or_specific_username_form_data)])
async def capture(username: str = Form(...), dataset_type: DatasetType = Form(...), detect_face: bool = Form(...),
                  files: List[Union[bytes, UploadFile]] = File(...)):
    result = {}
    for file in files:
        result = await datasets.save_raw_dataset(username, file, dataset_type)
    if detect_face:
        result = datasets.generate_datasets_from_raw_dir(username, dataset_type)
    return result


@router.post("/generate_datasets_from_raw", dependencies=[Depends(deps.get_current_admin)])
def generate_datasets_from_raw(params: schemas.GenerateDatasetParams):
    results = {}
    if len(params.usernames) == 1 and "student" in params.usernames:
        result = datasets.generate_datasets_from_folder_all(params.dataset_type, params.save_preprocessing)
        results = result
    else:
        total_users = 0
        total_datasets_raw = 0
        total_datasets = 0
        total_failed = 0
        total_rejected = 0
        computation_time = 0
        for i, username in enumerate(params.usernames):
            logger.info(f"{i + 1}/{len(params.usernames)}")
            logger.info("================================")
            result = datasets.generate_datasets_from_raw_dir(username, params.dataset_type, params.save_preprocessing)
            if result:
                total_users += 1
                total_datasets_raw += result["total_datasets_raw"]
                total_datasets += result["total_datasets"]
                total_failed += result["total_failed"]
                total_rejected += result["total_rejected"]
                computation_time += result["computation_time"]
        results["total_users"] = total_users
        results["total_datasets_raw"] = total_datasets_raw
        results["total_datasets"] = total_datasets
        results["total_failed"] = total_failed
        results["total_rejected"] = total_rejected
        results["computation_time"] = round(computation_time, 2)
        results["average_computation_time"] = round(computation_time / total_datasets, 2) if total_datasets > 0 else 0
    return results


@router.get("/total_datasets/{username}", dependencies=[Depends(deps.get_current_admin)])
def get_list_user_datasets(username: str):
    result = datasets.get_user_total_datasets_all(username)
    return result


@router.get("/{dataset_type}/{username}", dependencies=[Depends(deps.get_admin_or_specific_username)])
def get_list_user_datasets(dataset_type: DatasetType, username: str):
    list_datasets = datasets.get_user_datasets(username, dataset_type)
    return list_datasets


@router.delete('/{username}/{file_name}', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(deps.get_current_admin)])
def delete_dataset(username: str, file_name: str):
    return datasets.delete_user_dataset(username, file_name)
