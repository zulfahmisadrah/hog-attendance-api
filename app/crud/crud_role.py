from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.domains import Role
from app.models.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):

    def get_by_code(self, db: Session, *, code: str) -> Optional[Role]:
        return db.query(Role).filter(Role.code == code).first()


role = CRUDRole(Role)
