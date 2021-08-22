from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud
from app.models import domains, schemas
from app.api import deps
from app.core.config import settings
from app.resources import strings

router = APIRouter()


@router.get("/", response_model=List[schemas.User], dependencies=[Depends(deps.get_current_superuser)])
def index(db: Session = Depends(deps.get_db), offset: int = 0, limit: int = 10) -> Any:
    users = crud.user.get_list(db, offset=offset, limit=limit)
    return users


@router.post("/", response_model=schemas.User, dependencies=[Depends(deps.get_current_superuser)])
def create_user(user_in: schemas.UserCreate, db: Session = Depends(deps.get_db)) -> Any:
    user = crud.user.get_by_username(db, username=user_in.email)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.post("/create_superuser", response_model=schemas.User, dependencies=[Depends(deps.get_current_superuser)])
def create_superuser(user_in: schemas.UserCreate, db: Session = Depends(deps.get_db)) -> Any:
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    user = crud.user.create_superuser(db, obj_in=user_in)
    return user


@router.post("/create_admin", response_model=schemas.User, dependencies=[Depends(deps.get_current_superuser)])
def create_admin(user_in: schemas.UserCreate, db: Session = Depends(deps.get_db)) -> Any:
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    user = crud.user.create_admin(db, obj_in=user_in)
    return user


@router.post("/role/{role_id}", response_model=schemas.User, dependencies=[Depends(deps.get_current_superuser)])
def create_user(role_id: int, user_in: schemas.UserCreate, db: Session = Depends(deps.get_db)) -> Any:
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    user = crud.user.create(db, obj_in=user_in, role_id=role_id)
    return user


@router.get("/me", response_model=schemas.User, dependencies=[Depends(deps.get_db)])
def read_user_me(current_user: domains.User = Depends(deps.get_current_active_user)) -> Any:
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserUpdate,
        current_user: domains.User = Depends(deps.get_current_active_user)
) -> Any:
    current_user_data = jsonable_encoder(current_user)
    current_user_data.update((k, v) for k, v in user_in.dict().items() if v is not None)
    updated_user = schemas.UserUpdate(**current_user_data)
    user = crud.user.update(db, db_obj=current_user, obj_in=updated_user)
    return user


@router.post("/open", response_model=schemas.User, dependencies=[Depends(deps.get_current_superuser)])
def create_user_open(
        *,
        db: Session = Depends(deps.get_db),
        username: str = Body(...),
        password: str = Body(...),
        name: str = Body(...)
) -> Any:
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Open user registration is forbidden on this server"
        )
    user = crud.user.get_by_username(db, username=username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strings.USERNAME_TAKEN
        )
    user_in = schemas.UserCreate(username=username, password=password, name=name)
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=schemas.User, dependencies=[Depends(deps.get_current_superuser)])
def read_user_by_id(
        user_id: int,
        current_user: domains.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db),
) -> Any:
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}", response_model=schemas.User, dependencies=[Depends(deps.get_current_superuser)])
def update_user(
        *,
        db: Session = Depends(deps.get_db),
        user_id: int,
        user_in: schemas.UserUpdate,
        current_user: domains.User = Depends(deps.get_current_superuser)
) -> Any:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return current_user
