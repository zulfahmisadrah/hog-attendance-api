import json
from typing import Generic, TypeVar, Type

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.utils.file_helper import get_initial_data_file

ModelCRUD = TypeVar("ModelCRUD", bound=CRUDBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class DBSeeder(Generic[ModelCRUD, CreateSchemaType]):
    def __init__(self, db: Session, model_crud: Type[ModelCRUD], create_schema_type: Type[CreateSchemaType]):
        self.db = db
        self.crud = model_crud
        self.create_schema_type = create_schema_type

    def load_from_json(self, file_name: str):
        json_file = open(get_initial_data_file(file_name))
        print(f"-{file_name}...")
        for data_dict in json.load(json_file):
            data = self.crud.get(self.db, id=data_dict.get("id"))
            if not data:
                obj_in = self.create_schema_type(**data_dict)
                self.crud.create(self.db, obj_in=obj_in)
