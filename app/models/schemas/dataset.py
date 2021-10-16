from typing import List, Optional

from pydantic import BaseModel

from app.models.schemas import UserStudent


class Dataset(BaseModel):
    user: UserStudent
    file_names: List[str]
    total: int
    sample: Optional[bytes] = None
