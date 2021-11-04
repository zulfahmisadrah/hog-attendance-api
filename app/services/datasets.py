import io
import base64
import aiofiles
from os import path, remove
from typing import Union

from PIL import Image
import cv2
from fastapi import UploadFile

from app.ml.face_detection import detect_face, detect_face_on_image
from app.ml.datasets_training import train_datasets
from app.ml.face_recognition import recognize
from app.utils.file_helper import get_list_files, get_total_files, get_user_datasets_directory


def get_user_datasets(username: str):
    user_dir = get_user_datasets_directory(username)
    list_datasets = get_list_files(user_dir)
    return list_datasets


def generate_file_name(directory: str, username: str):
    files = get_list_files(directory)
    total_files = get_total_files(directory)
    list_numbers = [int(file.split('.')[1]) for file in files]
    missing_numbers = [x for x in range(1, total_files + 1) if x not in list_numbers]
    if missing_numbers:
        file_name = f"{username}.{missing_numbers[0]}.jpeg"
    else:
        file_name = f"{username}.{total_files + 1}.jpeg"
    return file_name


async def save_user_image(file: Union[bytes, UploadFile], username: str):
    user_dir = get_user_datasets_directory(username)
    file_name = generate_file_name(user_dir, username)
    file_path = path.join(user_dir, file_name)
    if isinstance(file, bytes):
        image_bytes = file[file.find(b'/9'):]
        image = Image.open(io.BytesIO(base64.b64decode(image_bytes)))
        image.resize((220, 220))
        image.save(file_path)
    else:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    detected_faces = detect_face(file_path)
    if detected_faces is not None:
        for detected_face in detected_faces:
            cv2.imwrite(file_path, detected_face)
    else:
        remove(file_path)
        file_path = None
    return file_path


def create_models(semester_code: str, course_code: str):
    file_path = train_datasets(semester_code, course_code)
    print("FILE PATH", file_path)
    return file_path


def recognize_face(file: bytes, semester_code: str, course_code: str):
    image_bytes = file[file.find(b'/9'):]
    image = Image.open(io.BytesIO(base64.b64decode(image_bytes)))
    image.resize((220, 220))
    detected_face, box = detect_face_on_image(image)
    recognized_user = recognize(detected_face, semester_code, course_code)
    print("RECOGNIZED USER", recognized_user)
    return recognized_user, box
