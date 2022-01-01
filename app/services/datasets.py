import io
import base64
import time
from os import path
from typing import Union

import aiofiles
from PIL import Image
import cv2
import numpy as np
from starlette.datastructures import UploadFile

from app.core.config import settings
from app.crud import crud_user
from app.db.session import SessionLocal
from app.ml.face_detection import detect_face_from_image_path, detect_face_on_image
from app.ml.datasets_training import train_datasets, validate_model
from app.ml.face_recognition import recognize
from app.services.image_processing import resize_image
from app.utils.commons import get_current_datetime
from app.utils.file_helper import get_list_files, get_total_files, get_user_datasets_directory, \
    get_user_datasets_raw_directory, get_dir


def get_user_datasets(username: str):
    user_dir = get_user_datasets_directory(username)
    list_datasets = get_list_files(user_dir)
    return list_datasets


def generate_file_name(directory: str, username: str):
    files = get_list_files(directory)
    total_files = get_total_files(directory)
    list_numbers = []
    for (i, file_name) in enumerate(files):
        split_file_name = file_name.split('.')
        if len(split_file_name) > 1:
            if split_file_name[1].isnumeric():
                number = int(split_file_name[1])
                list_numbers.append(number)
    missing_numbers = [x for x in range(1, total_files + 1) if x not in list_numbers]
    if missing_numbers:
        file_name = f"{username}.{missing_numbers[0]}.jpeg"
    else:
        file_name = f"{username}.{total_files + 1}.jpeg"
    return file_name


async def save_raw_dataset(file: Union[bytes, UploadFile], username: str):
    user_dir = get_user_datasets_raw_directory(username)
    file_name = generate_file_name(user_dir, username)
    file_path = path.join(user_dir, file_name)
    if isinstance(file, bytes):
        image_bytes = file[file.find(b'/9'):]
        image = Image.open(io.BytesIO(base64.b64decode(image_bytes)))
        image.save(file_path)
    else:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    list_images = get_list_files(user_dir)
    result = {
        "total_raw_datasets": len(list_images)
    }
    print("--------------------------------")
    print("FINISH SAVE IMAGES")
    print("RESULT", result)
    return result


def generate_datasets_from_folder(username: str, save_preprocessing=False):
    time_start = time.perf_counter()
    user_dir = get_user_datasets_raw_directory(username)
    list_images = get_list_files(user_dir)
    for (i, file_name) in enumerate(list_images):
        print("--------------------------------")
        print("IMAGE", i + 1)
        file_path = path.join(user_dir, file_name)
        detected_faces = detect_face_from_image_path(file_path, save_preprocessing=save_preprocessing)
        user_dataset_dir = get_user_datasets_directory(username)
        file_name = generate_file_name(user_dataset_dir, username)
        dataset_path = path.join(user_dataset_dir, file_name)
        if detected_faces:
            for detected_face in detected_faces:
                cv2.imwrite(dataset_path, detected_face)
    time_finish = time.perf_counter()
    estimated_time = time_finish - time_start
    result = {
        "computation_time": round(estimated_time, 2),
        "total_datasets": len(list_images)
    }
    print("--------------------------------")
    print("FINISH CREATING DATASET")
    print("RESULT", result)
    return result


def generate_datasets_from_folder_all():
    image_paths = get_list_files(settings.ASSETS_DATASETS_RAW_FOLDER)
    for username in image_paths:
        generate_datasets_from_folder(username)
    return "DONE"


def create_models(semester_code: str, course_code: str, validate: bool = False, save_preprocessing=False,
                  grid_search: bool = False):
    training_time_start = time.perf_counter()
    file_path = train_datasets(semester_code, course_code, save_preprocessing=False, grid_search=grid_search)
    training_time_finish = time.perf_counter()
    training_time = training_time_finish - training_time_start

    validating_time = 0
    accuracy = 0
    if validate:
        validating_time_start = time.perf_counter()
        accuracy = validate_model(semester_code, course_code, save_preprocessing)
        # file_path = validate_model(semester_code, course_code)
        validating_time_finish = time.perf_counter()
        validating_time = validating_time_finish - validating_time_start

    computation_time = training_time + validating_time
    accuracy = accuracy * 100
    result = {
        "file_path": file_path,
        "accuracy": round(accuracy, 2),
        "training_time": round(training_time, 2),
        "validating_time": round(validating_time, 2),
        "computation_time": round(computation_time, 2),
    }
    print("result", result)
    return result


def recognize_face(file: Union[bytes, UploadFile], semester_code: str, course_code: str):
    if isinstance(file, bytes):
        image_bytes = file[file.find(b'/9'):]
        image = Image.open(io.BytesIO(base64.b64decode(image_bytes)))
    else:
        content = file.file.read()
        image = Image.open(io.BytesIO(content))

    image = resize_image(image)

    detection_time_start = time.perf_counter()
    detected_faces = detect_face_on_image(image, return_box=True)
    detection_time_finish = time.perf_counter()
    detection_time = detection_time_finish - detection_time_start

    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    db = SessionLocal()

    recognition_time_start = time.perf_counter()
    predictions = []
    if detected_faces:
        for result in detected_faces:
            detected_face, box = result
            label = recognize(detected_face, semester_code, course_code)
            user = crud_user.user.get_by_username(db, username=label)
            user_name = user.name

            x, y, w, h = box
            x1, y1 = x + w, y + h
            cv2.rectangle(image, (x, y), (x1, y1), (0, 255, 0), 2)
            cv2.putText(image, user_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 10)
            cv2.putText(image, user_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

            prediction = {
                "username": label,
                "name": user_name
            }
            predictions.append(prediction)
            # print("RECOGNIZED USER", recognized_user)
    recognition_time_finish = time.perf_counter()
    recognition_time = recognition_time_finish - recognition_time_start

    current_datetime = get_current_datetime()
    result_dir = get_dir(settings.ASSETS_RESULT_FOLDER)
    image_name = f"{current_datetime}_{semester_code}_{course_code}.jpg"
    result_path = path.join(result_dir, image_name)
    cv2.imwrite(result_path, image)

    results = {
        "image_name": image_name,
        "predictions": predictions,
        "total_detection": len(detected_faces),
        "detection_time": detection_time,
        "recognition_time": recognition_time
    }
    print(results)
    return results
