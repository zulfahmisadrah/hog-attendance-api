import logging

from fastapi import FastAPI
from fastapi.security import HTTPBearer
from starlette.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from fastapi.logger import logger as fastapi_logger

gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

fastapi_logger.handlers = gunicorn_error_logger.handlers
if __name__ != "__main__":
    fastapi_logger.setLevel(logging.INFO)
    # fastapi_logger.setLevel(gunicorn_logger.level)
else:
    fastapi_logger.setLevel(logging.DEBUG)

security = HTTPBearer()
app = FastAPI()


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get('/')
def index():
    return {"messages": settings.PROJECT_NAME}
