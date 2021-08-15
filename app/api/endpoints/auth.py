from datetime import timedelta
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas, models, crud

from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login_access_token(
        db: Session = Depends(deps.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = crud.user.authenticate(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    payload = {
        "access_token": security.create_access_token(user.username, expires_delta=access_token_expires),
        "refresh_token": security.create_access_token(user.username, expires_delta=refresh_token_expires),
        "token_type": "Bearer"
    }
    return payload


@router.post("/check", response_model=schemas.User)
def check_access_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    return current_user
