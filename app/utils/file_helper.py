from typing import List
from os import path, listdir

from app.core.config import settings


def get_ml_models(file_name: str):
    return path.join(settings.ML_MODELS_FOLDER, file_name)


def get_initial_data_file(file_name: str):
    return path.join(settings.INITIAL_DATA_FOLDER, file_name)


def get_list_files(directory: str) -> List:
    return [file for file in listdir(directory)]


def get_total_files(directory: str) -> int:
    return len(get_list_files(directory))