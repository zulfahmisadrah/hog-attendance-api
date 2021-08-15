from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import schemas, models, crud

from app.api import deps
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def index(
        db: Session = Depends(deps.get_db),
        offset: int = 0,
        limit: int = 10,
        current_user: models.User = Depends(deps.get_current_superuser)
) -> Any:
    users = crud.user.get_list(db, offset=offset, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate,
        current_user: models.User = Depends(deps.get_current_superuser)
) -> Any:
    user = crud.user.get_by_username(db, username=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exist"
        )
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.post("/create_superuser", response_model=schemas.User)
def create_superuser(
        role_id: int,
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate,
        current_user: models.User = Depends(deps.get_current_superuser)
) -> Any:
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exist"
        )
    user = crud.user.create_superuser(db, obj_in=user_in)
    return user


@router.post("/create_admin", response_model=schemas.User)
def create_admin(
        role_id: int,
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate,
        current_user: models.User = Depends(deps.get_current_superuser)
) -> Any:
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exist"
        )
    user = crud.user.create_admin(db, obj_in=user_in)
    return user


@router.post("/role/{role_id}", response_model=schemas.User)
def create_user(
        role_id: int,
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate,
        current_user: models.User = Depends(deps.get_current_admin)
) -> Any:
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exist"
        )
    user = crud.user.create(db, obj_in=user_in, role_id=role_id)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
        *,
        db: Session = Depends(deps.get_db),
        username: str = Body(None),
        password: str = Body(None),
        name: str = Body(None),
        current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if username is not None:
        user_in.username = username
    if password is not None:
        user_in.password = password
    if name is not None:
        user_in.name = name
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.post("/open", response_model=schemas.User)
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
            detail="Username already exist"
        )
    user_in = schemas.UserCreate(username=username, password=password, name=name)
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
        user_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
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


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
        *,
        db: Session = Depends(deps.get_db),
        user_id: int,
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_superuser)
) -> Any:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return current_user