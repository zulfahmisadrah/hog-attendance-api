import argparse

import uvicorn
import logging

from fastapi import FastAPI
from fastapi.security import HTTPBearer
from starlette.middleware.cors import CORSMiddleware
from uvicorn.config import LOGGING_CONFIG

from app.api.routes import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
security = HTTPBearer()
app = FastAPI()

parser = argparse.ArgumentParser()
parser.add_argument('--seed', default=False, action='store_true', help="Seed database with initial data")
args = vars(parser.parse_args())


def init() -> None:
    db = SessionLocal()
    init_db(db)


def main() -> None:
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s %(levelprefix)s %(message)s"

    if args["seed"]:
        logger.info("Create initial data")
        init()
        logger.info("Initial data created")

    uvicorn.run("main:app", host=settings.WEB_HOST, port=settings.WEB_PORT, reload=settings.AUTO_RELOAD)


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


if __name__ == "__main__":
    main()
