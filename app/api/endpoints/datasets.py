from typing import List

from fastapi import File, APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import crud
from app.models import schemas
from app.api import deps
from app.db import session
from app.resources import strings
from app.services import datasets

router = APIRouter()


@router.get("/train", dependencies=[Depends(deps.get_current_admin)])
def train(db: Session = Depends(session.get_db)):
    datasets.create_models()
    # return {
    #     "file": FileResponse(file_path)
    # }


@router.post("/capture", dependencies=[Depends(deps.get_current_admin)])
def capture(student_id: int = Form(...), file: bytes = File(...), db: Session = Depends(session.get_db)):
    student = crud.student.get(db, student_id)
    file_path = datasets.save_user_image(file, student.user.username)
    return {
        "file": FileResponse(file_path)
    }


@router.get("/{student_id}", dependencies=[Depends(deps.get_current_admin)])
def get_list_user_datasets(student_id: int, db: Session = Depends(session.get_db)):
    student = crud.student.get(db, student_id)
    username = student.user.username
    list_datasets = datasets.get_user_datasets(username)
    return {"data": list_datasets}

