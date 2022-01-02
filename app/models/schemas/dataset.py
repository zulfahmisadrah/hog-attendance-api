from typing import List, Optional

from pydantic import BaseModel

from app.models.schemas import UserSimple
from app.resources.enums import DatasetType


class DatasetTotal(BaseModel):
    datasets_raw_train: int
    datasets_raw_val: int
    datasets_train: int
    datasets_val: int


class Dataset(BaseModel):
    user: UserSimple
    file_names: List[str]
    total: DatasetTotal
    sample: Optional[bytes] = None


class DatasetParams(BaseModel):
    username: str
    dataset_type: DatasetType = DatasetType.TRAINING


class GenerateDatasetParams(BaseModel):
    usernames: List[str] = []
    dataset_type: DatasetType = DatasetType.TRAINING
    save_preprocessing: bool = False


class TrainingParams(BaseModel):
    course_id: int
    save_preprocessing: bool = False
    deep_training: bool = False
    validate_model: bool = False
