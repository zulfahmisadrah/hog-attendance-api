from typing import List, Any, Union

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
    return crud.user.get_list(db, offset=offset, limit=limit)


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_superuser)])
def create_user(user_in: schemas.UserRolesCreate, db: Session = Depends(deps.get_db)) -> Any:
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    return crud.user.create(db, obj_in=user_in)


@router.post("/create_student", response_model=schemas.UserStudent, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_admin)])
def create_student(user_in: schemas.UserStudentCreate, db: Session = Depends(deps.get_db)) -> Any:
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    return crud.student.create(db, obj_in=user_in)


@router.post("/create_lecturer", response_model=schemas.UserLecturer, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.get_current_admin)])
def create_lecturer(user_in: schemas.UserLecturerCreate, db: Session = Depends(deps.get_db)) -> Any:
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    return crud.lecturer.create(db, obj_in=user_in)


@router.put("/me", response_model=schemas.User)
def update_user_me(
        user_in: schemas.UserUpdate,
        db: Session = Depends(deps.get_db),
        current_user: domains.User = Depends(deps.get_current_user)
) -> Any:
    if user_in.username and user_in.username != current_user.username:
        user = crud.user.get_by_username(db, username=user_in.username)
        if user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)
    current_user_data = schemas.UserUpdate(**jsonable_encoder(current_user))
    updated_user = current_user_data.copy(update=user_in.dict(exclude_unset=True))
    return crud.user.update(db, db_obj=current_user, obj_in=updated_user)


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


@router.get("/{user_id}", response_model=Union[schemas.UserStudent, schemas.UserLecturer, schemas.User])
def read_user_by_id(
        user_id: int,
        current_user: domains.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db),
) -> Any:
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_admin(current_user):
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
) -> Any:
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(deps.get_current_admin)])
def delete_user(user_id: int, db: Session = Depends(deps.get_db)):
    user = crud.user.get(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=strings.ERROR_DATA_ID_NOT_EXIST.format(user_id))
    return crud.user.delete(db, id=user_id)
