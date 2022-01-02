from typing import List
from os import path, listdir, mkdir

from app.core.config import settings
from app.resources.enums import DatasetType


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


def get_datasets_directory(dataset_type: DatasetType) -> str:
    return get_dir(path.join(get_dir(settings.ML_DATASETS_FOLDER), dataset_type))


def get_datasets_raw_directory(dataset_type: DatasetType) -> str:
    return get_dir(path.join(get_dir(settings.ML_DATASETS_RAW_FOLDER), dataset_type))


def get_user_datasets_directory(dataset_type: DatasetType, username: str) -> str:
    return get_dir(path.join(get_datasets_directory(dataset_type), username))


def get_user_datasets_raw_directory(dataset_type: DatasetType, username: str) -> str:
    return get_dir(path.join(get_datasets_raw_directory(dataset_type), username))


def get_preprocessed_images_directory(dataset_type: DatasetType) -> str:
    return get_dir(path.join(get_dir(settings.ML_PREPROCESSED_IMAGES_FOLDER), dataset_type))


def get_user_preprocessed_images_directory(dataset_type: DatasetType, username: str) -> str:
    return get_dir(path.join(get_preprocessed_images_directory(dataset_type), username))


def get_user_dataset_file(dataset_type: DatasetType, username: str, file_name: str) -> str:
    file_path = path.join(get_user_datasets_directory(dataset_type, username), file_name)
    return file_path


def get_course_models_directory(course_code: str) -> str:
    directory_path = path.join(get_dir(settings.ML_MODELS_FOLDER), course_code)
    return get_dir(directory_path)


def get_extracted_images_directory(username: str) -> str:
    directory_path = path.join(get_dir(settings.ML_EXTRACTED_IMAGES_FOLDER), username)
    return get_dir(directory_path)


def get_course_models_files(course_code: str) -> List:
    return listdir(get_course_models_directory(course_code))
