from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")


PROJECT_NAME = config("APP_NAME")
SQLALCHEMY_DATABASE_URI = config("DATABASE_URL")

API_PREFIX = "/api"

DEBUG = config("DEBUG", cast=bool, default=False)

DB_URL: str = config("DATABASE_URL")
HOST: str = config("HOST", default="127.0.0.1")
PORT: int = config("PORT", cast=int, default=3306)
USERNAME: str = config("USERNAME", default="root")
PASSWORD: str = config("PASSWORD", default="")
DB_NAME: str = config("DATABASE_NAME", default="")

SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret)