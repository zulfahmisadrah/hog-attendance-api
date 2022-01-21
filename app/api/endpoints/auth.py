from typing import Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud
from app.core.auth import auth
from app.models import domains, schemas

from app.api import deps

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
    token = schemas.Token(
        access_token=auth.encode_token(user.username),
        refresh_token=auth.encode_refresh_token(user.username),
        token_type="Bearer"
    )
    return token


@router.post("/refresh", response_model=schemas.Token)
def refresh_access_token(refresh_token: str = Form(...)) -> Any:
    new_token = auth.decode_refresh_token(refresh_token)
    token = schemas.Token(
        access_token=new_token,
        refresh_token=refresh_token,
        token_type="Bearer"
    )
    return token


@router.post("/me", response_model=Union[schemas.UserStudent, schemas.UserLecturer, schemas.User])
def check_access_token(current_user: domains.User = Depends(deps.get_current_user)) -> Any:
    return current_user
