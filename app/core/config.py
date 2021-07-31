import secrets
from typing import List, Union

from pydantic import BaseSettings, AnyHttpUrl, validator, EmailStr
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")


PROJECT_NAME = config("APP_NAME")
SQLALCHEMY_DATABASE_URI = config("DB_URL")

API_PREFIX = "/api"

DEBUG = config("DEBUG", cast=bool, default=False)

DB_URL: str = config("DB_URL")
HOST: str = config("DB_HOST", default="127.0.0.1")
PORT: int = config("DB_PORT", cast=int, default=3306)
USERNAME: str = config("DB_USERNAME", default="root")
PASSWORD: str = config("DB_PASSWORD", default="")
DB_NAME: str = config("DB_NAME", default="")

SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret)


class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ['http://localhost:3000']

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    FIRST_SUPERUSER: str = "sadmin"
    FIRST_SUPERUSER_PASSWORD: str = "123456"
    USERS_OPEN_REGISTRATION: bool = False

    class Config:
        case_sensitive = True


settings = Settings()