import base64
from typing import Any

from os import path, remove
from fastapi import status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import crud_user
from app.models.schemas import Dataset
from app.services import get_user_datasets
from app.utils.file_helper import get_list_files, get_user_dataset_file, get_dir


def get_list_datasets(db: Session):
    list_username = get_list_files(get_dir(settings.DATASETS_FOLDER))
    list_datasets = []
    for username in list_username:
        student = crud_user.user.get_by_username(db, username=username)
        user_datasets = get_user_datasets(username)
        if user_datasets:
            # sample_image_path = user_datasets[0]
            sample_image_path = path.join(settings.DATASETS_FOLDER, username, user_datasets[0])
            with open(sample_image_path, "rb") as imageFile:
                sample = base64.b64encode(imageFile.read())
            payload = Dataset(
                user=student,
                file_names=user_datasets,
                total=len(user_datasets),
                sample=sample)
            list_datasets.append(payload)
    return list_datasets


def delete_user_dataset(username: str, file_name: str) -> Any:
    file_path = get_user_dataset_file(username, file_name)
    remove(file_path)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
