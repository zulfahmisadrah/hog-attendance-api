from typing import List
from os import path, listdir, mkdir

from app.core.config import settings


def create_directory_if_not_exist(directory: str) -> str:
    if not path.isdir(directory):
        mkdir(directory)
    return directory


def get_list_files(directory: str) -> List:
    return listdir(directory)


def get_total_files(directory: str) -> int:
    return len(get_list_files(directory))


def get_initial_data_file(file_name: str) -> str:
    return path.join(settings.INITIAL_DATA_FOLDER, file_name)


def get_user_datasets_directory(username: str) -> str:
    directory = path.join(settings.DATASETS_FOLDER, username)
    directory = create_directory_if_not_exist(directory)
    return directory


def get_course_models_directory(course_code: str) -> str:
    directory = path.join(settings.ML_MODELS_FOLDER, course_code)
    directory = create_directory_if_not_exist(directory)
    return directory


def get_hog_outputs_directory(username: str) -> str:
    directory = path.join(settings.ML_OUTPUTS_FOLDER, username)
    directory = create_directory_if_not_exist(directory)
    return directory


def get_course_models_files(course_code: str) -> List:
    return listdir(get_course_models_directory(course_code))
