from typing import Optional

from pydantic import BaseModel

from app.enums.setting_type import SettingType
from app.models.schemas.core import DateTimeModelMixin, IDMixin


class SiteSettingBase(BaseModel):
    setting_type: SettingType
    setting_value: Optional[str] = None
    created_by_id: Optional[int] = None
    modified_by_id: Optional[int] = None


class SiteSettingCreate(SiteSettingBase):
    created_by_id: int


class SiteSettingUpdate(SiteSettingBase):
    modified_by_id: int


class SiteSetting(DateTimeModelMixin, SiteSettingBase, IDMixin):
    pass
