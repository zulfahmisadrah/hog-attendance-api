from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.utils.file_helper import get_avatar_file, get_user_dataset_file

router = APIRouter()


@router.get("/avatar/{file_name}")
def get_avatar(file_name: str):
    avatar = get_avatar_file(file_name)
    return FileResponse(avatar)


@router.get("/dataset/{username}/{file_name}")
def get_dataset(username: str, file_name: str):
    dataset = get_user_dataset_file(username, file_name)
    return FileResponse(dataset)
