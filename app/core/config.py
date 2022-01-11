import os
import secrets
from typing import List, Union, Tuple

from pydantic import BaseSettings, AnyHttpUrl, validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "PROJECT")

    INITIAL_DATA_FOLDER: str = os.path.join("app", "db", "data")
    ASSETS_AVATAR_FOLDER: str = os.path.join("app", "assets", "avatar")
    ASSETS_RESULT_FOLDER: str = os.path.join("app", "assets", "result")
    # ML_DATASETS_RAW_FOLDER: str = os.path.join("app", "ml", "datasets_raw")
    ML_DATASETS_RAW_FOLDER: str = os.path.join("app", "ml", "datasets_raw_mask_3")
    # ML_DATASETS_RAW_FOLDER: str = os.path.join("app", "ml", "datasets_raw_mask_only_3")
    ML_DATASETS_RAW_TRAIN_FOLDER: str = os.path.join(ML_DATASETS_RAW_FOLDER, "train")
    ML_DATASETS_RAW_VAL_FOLDER: str = os.path.join(ML_DATASETS_RAW_FOLDER, "val")
    # ML_DATASETS_FOLDER: str = os.path.join("app", "ml", "datasets")
    ML_DATASETS_FOLDER: str = os.path.join("app", "ml", "datasets_mask")
    # ML_DATASETS_FOLDER: str = os.path.join("app", "ml", "datasets_mask_only")
    ML_DATASETS_TRAIN_FOLDER: str = os.path.join(ML_DATASETS_FOLDER, "train")
    ML_DATASETS_VAL_FOLDER: str = os.path.join(ML_DATASETS_FOLDER, "val")
    ML_EXTRACTED_IMAGES_FOLDER: str = os.path.join("app", "ml", "extracted_images")
    # ML_MODELS_FOLDER: str = os.path.join("app", "ml", "models")
    # ML_MODELS_FOLDER: str = os.path.join("app", "ml", "models_mask")
    # ML_MODELS_FOLDER: str = os.path.join("app", "ml", "models_mask_only")
    ML_MODELS_FOLDER: str = os.path.join("app", "ml", "models_f")
    # ML_MODELS_FOLDER: str = os.path.join("app", "ml", "models_mask_f")
    # ML_MODELS_FOLDER: str = os.path.join("app", "ml", "models_mask_only_f")
    ML_TEST_FOLDER: str = os.path.join("app", "ml", "test")
    ML_PREPROCESSED_IMAGES_FOLDER: str = os.path.join("app", "ml", "preprocessed_images")
    ML_MODEL_FACENET: str = os.path.join("app", "ml", "pretrained_models", "facenet_keras", "facenet_keras.h5")
    ML_PLOTS_FOLDER: str = os.path.join("app", "ml", "plots")
    USE_FACENET: bool = True
    # USE_FACENET: bool = False

    IMAGE_MAX_SIZE: int = 1600
    IMAGE_ALPHA: float = 1.5  # Contrast control (1.0-3.0)
    IMAGE_BETA: float = 10  # Brightness control (0-100)

    HOG_ORIENTATIONS: int = 9
    HOG_PIXELS_PER_CELL: Tuple[int, int] = (10, 10)
    HOG_CELLS_PER_BLOCK: Tuple[int, int] = (2, 2)
    HOG_RESIZE_WIDTH: int = 90
    HOG_RESIZE_HEIGHT: int = 90
    FACENET_INPUT_SIZE: Tuple[int, int] = (160, 160)

    WEB_HOST: str = os.getenv("WEB_HOST", "127.0.0.1")
    WEB_PORT: int = os.getenv("WEB_PORT", 8000)
    AUTO_RELOAD: bool = os.getenv("DEBUG", False)

    DEBUG: bool = os.getenv("DEBUG", False)

    API_PREFIX: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440
    # BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ['http://localhost:3000', 'http://192.168.1.16:3000/']
    BACKEND_CORS_ORIGINS: List[str] = ['*']

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    DB_USERNAME: str = os.getenv("DB_USERNAME", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = os.getenv("DB_PORT", 3306)
    DB_NAME: str = os.getenv("DB_NAME", "app")

    SQLALCHEMY_DATABASE_URI: str = f"mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    FIRST_SUPERUSER_NAME: str = os.getenv("FIRST_SUPERUSER_NAME", "admin")
    FIRST_SUPERUSER_USERNAME: str = os.getenv("FIRST_SUPERUSER_USERNAME", "admin")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "123456")
    USERS_OPEN_REGISTRATION: bool = False

    class Config:
        case_sensitive = True


settings = Settings()
