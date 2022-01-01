from typing import List, Optional

from pydantic import BaseModel

from app.models.schemas import UserStudent


class Dataset(BaseModel):
    user: UserStudent
    file_names: List[str]
    total: int
    sample: Optional[bytes] = None


class DatasetParams(BaseModel):
    username: str
    save_preprocessing: bool = False


class TrainingParams(BaseModel):
    course_id: int
    save_preprocessing: bool = False
    deep_training: bool = False
    validate_model: bool = False
