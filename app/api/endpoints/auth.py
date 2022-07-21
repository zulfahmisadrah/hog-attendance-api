import logging
import hashlib
from typing import Any, Union
from ast import literal_eval

import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from suds.client import Client
from suds.transport.http import HttpAuthenticated

from app import crud
from app.core.auth import auth
from app.core.config import settings
from app.models import domains, schemas

from app.api import deps
from app.utils.commons import parse_year_from_username

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)


@router.post("/login", response_model=schemas.Token)
def login_access_token(
        db: Session = Depends(deps.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    username = form_data.username
    password = form_data.password
    user = crud.user.authenticate(db, username=username, password=password)
    if not user:
        # LECTURER
        transport = HttpAuthenticated(username=settings.NEOSIA_SOAP_USERNAME, password=settings.NEOSIA_SOAP_PASSWORD)
        soap_client = Client(settings.NEOSIA_SOAP_BASE_URL, transport=transport, timeout=10)
        result = soap_client.service.login2(username, hashlib.md5(password.encode()).hexdigest())
        if result != "[]":
            result = literal_eval(result)
            username = result.get("userAccount")
            name = result.get("userNama")
            user_local = crud.user.get_by_username(db, username=username)
            if user_local:
                user = user_local
            else:
                department = crud.department.get_by_username_parsing(db, username)
                user_in = schemas.UserLecturerCreate(
                    name=name,
                    username=username,
                    password=password,
                    lecturer=schemas.LecturerCreate(department_id=department.id if department else 12,
                                                    nip=username)
                )
                user = crud.user.create_lecturer(db, obj_in=user_in)
        else:
            # STUDENT
            with httpx.Client() as client:
                headers = {
                    'token': settings.NEOSIA_API_HEADER_TOKEN,
                    'Content-Type': "application/x-www-form-urlencoded",
                }
                data = {
                    "username": username,
                    "password": password
                }
                response = client.post(settings.NEOSIA_API_AUTH_STUDENT, data=data, headers=headers)
                result = response.json()['success']
                if result == "1":
                    user_local = crud.user.get_by_username(db, username=username)
                    if user_local:
                        user = user_local
                    else:
                        department = crud.department.get_by_username_parsing(db, username)
                        user_in = schemas.UserStudentCreate(
                            name=username,
                            username=username,
                            password=password,
                            student=schemas.StudentCreate(department_id=department.id,
                                                          year=parse_year_from_username(username))
                        )
                        user = crud.user.create_student(db, obj_in=user_in)
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Incorrect username or password")
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
