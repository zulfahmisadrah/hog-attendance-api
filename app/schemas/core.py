from typing import Optional
from datetime import datetime

from pydantic import BaseModel, validator


class CoreModel(BaseModel):
    id: int
    pass


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @validator("created_at", "updated_at", pre=True)
    def default_datetime(self, value: datetime) -> datetime:
        return value or datetime.datetime.now()