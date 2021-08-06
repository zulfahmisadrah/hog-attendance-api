from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import crud_user
from app.schemas.user import UserCreate


def init_db(db: Session) -> None:
    user = crud_user.user.get_by_username(db, username=settings.FIRST_SUPERUSER_USERNAME)
    if not user:
        user_in = UserCreate(
            name=settings.FIRST_SUPERUSER_NAME,
            username=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True
        )
        user = crud_user.user.create(db, obj_in=user_in)
