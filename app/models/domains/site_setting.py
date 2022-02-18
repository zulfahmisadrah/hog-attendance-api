from sqlalchemy import Column, String, BigInteger, ForeignKey

from app.db.base_class import Base
from app.models.domains.core import CommonModel


class SiteSetting(Base, CommonModel):
    setting_type = Column(String(255), nullable=False)
    setting_value = Column(String(255), nullable=False)
    created_by_id = Column(BigInteger, ForeignKey("user.id"))
    modified_by_id = Column(BigInteger, ForeignKey("user.id"))
