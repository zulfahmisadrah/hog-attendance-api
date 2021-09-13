from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_permissions import Everyone, Authenticated, configure_permissions
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud
from app.models import domains
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/login",
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> domains.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception
    user = crud.user.get_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: domains.User = Depends(get_current_user)) -> domains.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is inactive")
    return current_user


def get_current_superuser(current_user: domains.User = Depends(get_current_active_user)) -> domains.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User doesn't have enough privileges")
    return current_user


def get_current_admin(current_user: domains.User = Depends(get_current_active_user)) -> domains.User:
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User doesn't have enough privileges")
    return current_user


def get_active_semester(db: Session = Depends(get_db)) -> domains.Semester:
    return crud.semester.get_active_semester(db)


def get_active_principals(user: domains.User = Depends(get_current_active_user)):
    if user:
        # user is logged in
        principals = [Everyone, Authenticated]
        principals.extend(getattr(user, "username", ""))
        principals.extend(getattr(user, "role", []))
    else:
        # user is NOT logged in
        principals = [Everyone]
    return principals


Permission = configure_permissions(get_active_principals)
