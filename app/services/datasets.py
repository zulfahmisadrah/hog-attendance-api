import io
import base64
import time
import json
from fastapi.logger import logger
from typing import Union, Any
from os import path, remove

import cv2
import aiofiles
import numpy as np
from PIL import Image
from fastapi import status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile

from app.core.config import settings
from app.crud import crud_user, crud_site_setting
from app.enums.setting_type import SettingType
from app.models.schemas import Dataset, DatasetTotal
from app.ml.face_detection import detect_face_on_image
from app.ml.datasets_training import train_datasets, validate_model, validate_model_using_train_data
from app.resources.enums import DatasetType
from app.utils.commons import get_current_datetime
from app.utils.file_helper import get_list_files, get_total_files, get_user_datasets_directory, \
    get_user_datasets_raw_directory, get_dir, get_user_dataset_file, get_datasets_directory, get_datasets_raw_directory, \
    generate_file_name, get_user_preprocessed_images_directory, clear_files_in_dir, get_meeting_results_directory


def get_user_datasets(username: str, dataset_type: DatasetType = DatasetType.TRAINING):
    user_dir = get_user_datasets_directory(dataset_type, username)
    list_datasets = get_list_files(user_dir)
    return list_datasets


def get_user_datasets_raw(username: str, dataset_type: DatasetType = DatasetType.TRAINING):
    user_dir = get_user_datasets_raw_directory(dataset_type, username)
    list_datasets = get_list_files(user_dir)
    return list_datasets


def get_user_total_datasets_all(username: str) -> DatasetTotal:
    total_datasets_raw_train = get_total_files(get_user_datasets_raw_directory(DatasetType.TRAINING, username))
    total_datasets_raw_val = get_total_files(get_user_datasets_raw_directory(DatasetType.VALIDATION, username))
    total_datasets_train = get_total_files(get_user_datasets_directory(DatasetType.TRAINING, username))
    total_datasets_val = get_total_files(get_user_datasets_directory(DatasetType.VALIDATION, username))
    total = DatasetTotal(
        datasets_raw_train=total_datasets_raw_train,
        datasets_raw_val=total_datasets_raw_val,
        datasets_train=total_datasets_train,
        datasets_val=total_datasets_val
    )
    return total


def get_user_sample_dataset(username: str, dataset_type: DatasetType = DatasetType.TRAINING):
    sample = None
    user_datasets = get_user_datasets(username)
    if user_datasets:
        user_datasets.sort()
        # sample_image_path = user_datasets[0]
        sample_image_path = get_user_dataset_file(dataset_type, username, user_datasets[0])
        with open(sample_image_path, "rb") as imageFile:
            sample = base64.b64encode(imageFile.read())
    return sample


async def save_raw_dataset(username: str, file: Union[bytes, UploadFile],
                           dataset_type: DatasetType = DatasetType.TRAINING):
    user_dir = get_user_datasets_raw_directory(dataset_type, username)
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
        "image_name": file_name,
        "total_raw_datasets": len(list_images)
    }
    logger.info("--------------------------------")
    logger.info("FINISH SAVE IMAGES")
    logger.info("RESULT " + str(result))
    return result


def generate_datasets_from_raw_dir(username: str, dataset_type: DatasetType = DatasetType.TRAINING,
                                   save_preprocessing=False):
    user_dir = get_user_datasets_raw_directory(dataset_type, username)
    list_datasets_raw = get_list_files(user_dir)
    if not list_datasets_raw:
        return None
    list_datasets_raw.sort()

    user_dataset_dir = get_user_datasets_directory(dataset_type, username)
    total_datasets = get_total_files(user_dataset_dir)
    total_rejected = 0
    if total_datasets > 0:
        clear_files_in_dir(user_dataset_dir)

    if save_preprocessing:
        preprocessed_dir = get_user_preprocessed_images_directory(dataset_type, username)
        total_images = get_total_files(preprocessed_dir)
        if total_images > 0:
            clear_files_in_dir(preprocessed_dir)
    else:
        preprocessed_dir = get_dir(settings.ML_PREPROCESSED_IMAGES_FOLDER)

    time_start = time.perf_counter()
    for (i, file_name) in enumerate(list_datasets_raw):
        logger.info("--------------------------------")
        logger.info(f"IMAGE {i + 1}/{len(list_datasets_raw)} of {username}")
        file_path = path.join(user_dir, file_name)
        detection_result = detect_face_on_image(file_path, save_path=preprocessed_dir, multiple_faces=False,
                                                save_preprocessing=save_preprocessing)
        detected_faces = detection_result["detected_faces"]
        total_rejected = total_rejected + detection_result["total_rejected"]
        file_name = generate_file_name(user_dataset_dir, username)
        dataset_path = path.join(user_dataset_dir, file_name)
        if detected_faces:
            for detected_face in detected_faces:
                cv2.imwrite(dataset_path, detected_face)
    time_finish = time.perf_counter()
    estimated_time = time_finish - time_start

    total_datasets = get_total_files(user_dataset_dir)
    result = {
        "computation_time": round(estimated_time, 2),
        "total_datasets_raw": len(list_datasets_raw),
        "total_datasets": total_datasets,
        "total_failed": len(list_datasets_raw) - total_datasets,
        "total_rejected": total_rejected
    }
    logger.info("--------------------------------")
    logger.info("FINISH CREATING DATASET")
    logger.info("RESULT " + str(result))
    return result


def generate_datasets_from_folder_all(dataset_type: DatasetType = DatasetType.TRAINING, save_preprocessing=False):
    list_datasets_raw = get_list_files(get_datasets_raw_directory(dataset_type))
    total_users = 0
    total_datasets_raw = 0
    total_datasets = 0
    total_failed = 0
    total_rejected = 0
    computation_time = 0
    for i, username in enumerate(list_datasets_raw):
        logger.info(f"{i + 1}/{len(list_datasets_raw)}")
        logger.info("================================")
        result = generate_datasets_from_raw_dir(username, dataset_type, save_preprocessing)
        if result:
            total_users += 1
            total_datasets_raw += result["total_datasets_raw"]
            total_datasets += result["total_datasets"]
            total_failed += result["total_failed"]
            total_rejected += result["total_rejected"]
            computation_time += result["computation_time"]
    result = {
        "total_users": total_users,
        "total_datasets_raw": total_datasets_raw,
        "total_datasets": total_datasets,
        "total_failed": total_failed,
        "total_rejected": total_rejected,
        "computation_time": round(computation_time, 2),
        "average_computation_time": round(computation_time / total_datasets, 2) if total_datasets > 0 else 0
    }
    return result


def create_models(db: Session, semester_code: str, course_code: str, validate: bool = False, save_preprocessing=False,
                  grid_search: bool = False):
    params_key = crud_site_setting.site_setting.get_setting(db, setting_type=SettingType.ML_PARAMS_KEY).setting_value
    training_time_start = time.perf_counter()
    if grid_search:
        file_path, score = train_datasets(db, semester_code, course_code, save_preprocessing, grid_search,
                                          return_score=grid_search, params_key=params_key)
    else:
        file_path = train_datasets(db, semester_code, course_code, save_preprocessing, grid_search,
                                   params_key=params_key)
    training_time_finish = time.perf_counter()
    training_time = training_time_finish - training_time_start

    validating_time = 0
    accuracy = 0
    if validate:
        validating_time_start = time.perf_counter()
        accuracy = validate_model(db, semester_code, course_code, save_preprocessing, params_key=params_key)
        validating_time_finish = time.perf_counter()
        validating_time = validating_time_finish - validating_time_start
    else:
        validating_time_start = time.perf_counter()
        accuracy = score if grid_search else validate_model_using_train_data(db, semester_code, course_code, save_preprocessing, params_key=params_key)
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
    logger.info("result " + str(result))
    return result


def recognize_face(db: Session, file: Union[bytes, UploadFile], semester_code: str, course_code: str, meeting_id: int,
                   save_preprocessing=False):
    if isinstance(file, bytes):
        image_bytes = file[file.find(b'/9'):]
        image = Image.open(io.BytesIO(base64.b64decode(image_bytes)))
    else:
        content = file.file.read()
        image = Image.open(io.BytesIO(content))

    # image = resize_image_if_too_big(image)

    detection_time_start = time.perf_counter()
    detection_result = detect_face_on_image(image, resize_image=False, return_box=True,
                                            save_preprocessing=save_preprocessing, recognize_face=True,
                                            semester_code=semester_code, course_code=course_code)
    detected_faces = detection_result["detected_faces"]
    detection_time_finish = time.perf_counter()
    detection_time = detection_time_finish - detection_time_start

    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    recognition_time_start = time.perf_counter()
    predictions = []
    if detected_faces:
        for result in detected_faces:
            detected_face, box, label = result
            user = crud_user.user.get_by_username(db, username=label)
            user_name = user.name

            x, y, w, h = box
            x1, y1 = x + w, y + h

            width = image.shape[1]
            if width > 4000:
                font_scale = 2.4
                thickness_white = 30
                thickness_black = 6
            elif width > 2500:
                font_scale = 1.5
                thickness_white = 15
                thickness_black = 4
            elif width > 1500:
                font_scale = 0.8
                thickness_white = 8
                thickness_black = 2
            else:
                font_scale = 0.3
                thickness_white = 4
                thickness_black = 1
            cv2.rectangle(image, (x, y), (x1, y1), (0, 255, 0), 2)
            cv2.putText(image, user_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness_white)
            cv2.putText(image, user_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness_black)

            prediction = {
                "username": label,
                "name": user_name
            }
            predictions.append(prediction)
            # logger.info("RECOGNIZED USER", recognized_user)
    recognition_time_finish = time.perf_counter()
    recognition_time = recognition_time_finish - recognition_time_start

    current_datetime = get_current_datetime()
    result_dir = get_meeting_results_directory(semester_code, course_code, meeting_id)
    image_name = f"{current_datetime}_{semester_code}_{course_code}.jpg"
    result_path = path.join(result_dir, image_name)
    cv2.imwrite(result_path, image)

    results = {
        "image_name": image_name,
        "predictions": predictions,
        "total_detection": len(detected_faces),
        "detection_time": round(detection_time, 2),
        "recognition_time": round(recognition_time, 2),
        "computation_time": round(recognition_time + detection_time, 2)
    }
    logger.info(results)
    return results


def get_list_datasets(db: Session, dataset_type: DatasetType = DatasetType.TRAINING):
    list_username = get_list_files(get_datasets_directory(dataset_type))
    list_datasets = []
    for username in list_username:
        student = crud_user.user.get_by_username(db, username=username)
        user_datasets = get_user_datasets(username)
        total = get_user_total_datasets_all(username)
        dataset = Dataset(
            user=student,
            file_names=user_datasets,
            total=total,
        )
        list_datasets.append(dataset)
    return list_datasets


def delete_user_dataset(username: str, file_name: str, dataset_type: DatasetType = DatasetType.TRAINING) -> Any:
    file_path = get_user_dataset_file(dataset_type, username, file_name)
    remove(file_path)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
