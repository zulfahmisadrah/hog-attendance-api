from typing import Optional
from datetime import datetime, timezone

from pydantic import BaseModel, validator, BaseConfig


def convert_datetime_to_iso_format(dt: datetime) -> str:
    return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class Model(BaseModel):
    class Config(BaseConfig):
        json_encoders = {datetime: convert_datetime_to_iso_format}


class ModelORM(Model):
    class Config(Model.Config):
        orm_mode = True


class IDMixin(BaseModel):
    id: int


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator("created_at", "updated_at", pre=True)
    def default_datetime(cls, value: datetime) -> datetime:
        return value or datetime.now()
