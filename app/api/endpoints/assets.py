from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.resources.enums import DatasetType
from app.utils.file_helper import get_avatar_file, get_user_dataset_file, get_result_file

router = APIRouter()


@router.get("/avatar/{file_name}")
def get_avatar(file_name: str):
    avatar = get_avatar_file(file_name)
    return FileResponse(avatar)


@router.get("/dataset/{dataset_type}/{username}/{file_name}")
def get_dataset(dataset_type: DatasetType, username: str, file_name: str):
    dataset = get_user_dataset_file(dataset_type, username, file_name)
    return FileResponse(dataset)


@router.get("/result/{file_name}")
def get_result(file_name: str):
    result = get_result_file(file_name)
    return FileResponse(result)
