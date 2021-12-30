from typing import List
from os import path, listdir, mkdir

from app.core.config import settings


def create_directory_if_not_exist(directory: str) -> str:
    if not path.isdir(directory):
        mkdir(directory)
    return directory


def get_dir(dir_path: str) -> str:
    return create_directory_if_not_exist(dir_path)


def get_list_files(directory: str) -> List:
    return listdir(directory)


def get_total_files(directory: str) -> int:
    return len(get_list_files(directory))


def get_initial_data_file(file_name: str) -> str:
    return path.join(settings.INITIAL_DATA_FOLDER, file_name)


def get_avatar_file(file_name: str) -> str:
    return path.join(settings.ASSETS_AVATAR_FOLDER, file_name)


def get_result_file(file_name: str) -> str:
    return path.join(settings.ASSETS_RESULT_FOLDER, file_name)


def get_user_datasets_directory(username: str) -> str:
    directory_path = path.join(get_dir(settings.DATASETS_FOLDER), username)
    return get_dir(directory_path)


def get_user_datasets_raw_directory(username: str) -> str:
    directory_path = path.join(get_dir(settings.ASSETS_DATASETS_RAW_FOLDER), username)
    return get_dir(directory_path)


def get_user_validation_directory(username: str) -> str:
    directory_path = path.join(get_dir(settings.ML_VALIDATION_FOLDER), username)
    return get_dir(directory_path)


def get_user_dataset_file(username: str, file_name: str) -> str:
    file_path = path.join(get_dir(settings.DATASETS_FOLDER), username, file_name)
    return file_path


def get_course_models_directory(course_code: str) -> str:
    directory_path = path.join(get_dir(settings.ML_MODELS_FOLDER), course_code)
    return get_dir(directory_path)


def get_extracted_images_directory(username: str) -> str:
    directory_path = path.join(get_dir(settings.ML_EXTRACTED_IMAGES_FOLDER), username)
    return get_dir(directory_path)


def get_course_models_files(course_code: str) -> List:
    return listdir(get_course_models_directory(course_code))
