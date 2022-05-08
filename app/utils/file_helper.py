from shutil import rmtree
from typing import List
from os import path, listdir, makedirs

from app.core.config import settings
from app.crud import crud_site_setting
from app.db.session import SessionLocal
from app.resources.enums import DatasetType


def create_directory_if_not_exist(directory: str) -> str:
    if not path.isdir(directory):
        makedirs(directory)
    return directory


def get_dir(dir_path: str) -> str:
    return create_directory_if_not_exist(dir_path)


def get_list_files(directory: str) -> List[str]:
    return listdir(directory)


def get_total_files(directory: str) -> int:
    return len(get_list_files(directory))


def clear_files_in_dir(directory: str):
    rmtree(directory)
    makedirs(directory)


def get_file_name_without_extension(filename: str):
    return path.splitext(filename)[0] or filename


def get_initial_data_file(file_name: str) -> str:
    return path.join(settings.INITIAL_DATA_FOLDER, file_name)


def get_avatar_file(file_name: str) -> str:
    return path.join(settings.ASSETS_AVATAR_FOLDER, file_name)


def get_meeting_results_directory(semester_code: str, course_code: str, meeting_id: int) -> str:
    return get_dir(path.join(settings.ASSETS_RESULT_FOLDER, semester_code, course_code, str(meeting_id)))


def get_result_file(semester_code: str, course_code: str, meeting_id: int, file_name: str) -> str:
    return path.join(get_meeting_results_directory(semester_code, course_code, meeting_id), file_name)


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


def get_user_dataset_raw_file(dataset_type: DatasetType, username: str, file_name: str) -> str:
    file_path = path.join(get_user_datasets_raw_directory(dataset_type, username), file_name)
    return file_path


def get_course_models_directory(course_code: str) -> str:
    db = SessionLocal()
    use_facenet = crud_site_setting.site_setting.use_facenet(db)
    model_dir = settings.ML_MODELS_FOLDER_FACENET if use_facenet else settings.ML_MODELS_FOLDER
    directory_path = path.join(get_dir(model_dir), course_code)
    return get_dir(directory_path)


def get_extracted_images_directory(username: str) -> str:
    directory_path = path.join(get_dir(settings.ML_EXTRACTED_IMAGES_FOLDER), username)
    return get_dir(directory_path)


def get_course_models_files(course_code: str) -> List:
    return listdir(get_course_models_directory(course_code))


def generate_file_name(directory: str, username: str, extension: str = ".jpeg"):
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
        file_name = f"{username}.{missing_numbers[0]}{extension}"
    else:
        file_name = f"{username}.{total_files + 1}{extension}"
    return file_name
