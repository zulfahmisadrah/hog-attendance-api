from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.enums.setting_type import SettingType
from app.models.domains import SiteSetting
from app.models.schemas import SiteSettingCreate, SiteSettingUpdate


class CRUDSiteSetting(CRUDBase[SiteSetting, SiteSettingCreate, SiteSettingUpdate]):
    def get_all_by_setting_type(self, db: Session, *, setting_type: SettingType) -> List[SiteSetting]:
        return db.query(self.model).filter(self.model.setting_type == setting_type).all()

    def get_setting(self, db: Session, *, setting_type: SettingType) -> SiteSetting:
        return db.query(self.model).filter(self.model.setting_type == setting_type).first()

    def update_setting(self, db: Session, *, setting_type: SettingType, setting_value: str) -> SiteSetting:
        data = db.query(self.model).filter(self.model.setting_type == setting_type).first()
        data.update({self.model.setting_value: setting_value})
        db.commit()
        db.refresh(data)
        return data

    def use_facenet(self, db: Session) -> bool:
        setting_recognition_method = self.get_setting(db, setting_type=SettingType.ML_FACE_RECOGNITION_METHOD)
        return setting_recognition_method.setting_value == "FACENET"

    def datasets_with_mask(self, db: Session) -> bool:
        setting_recognition_method = self.get_setting(db, setting_type=SettingType.ML_DATASETS_WITH_MASK)
        return setting_recognition_method.setting_value == "1"


site_setting = CRUDSiteSetting(SiteSetting)
