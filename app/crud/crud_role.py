from typing import Optional, Union, Dict, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):

    def get_by_code(self, db: Session, *, code: str) -> Optional[Role]:
        return db.query(Role).filter(Role.code == code).first()


role = CRUDRole(Role)
