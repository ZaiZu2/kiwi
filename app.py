from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from config import LOGGING_CONFIG, get_config
from src.api import main, rooms
from src.database import create_root_objects, recreate_database
from src.dependencies import get_connection_manager
from src.utils import expire_inactive_rooms, schedule_recurring_task, tags_metadata
from src.cache import request_validation_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    if get_config().ENVIRONMENT == 'development':
        await recreate_database()
        await create_root_objects()

    yield


def create_app() -> FastAPI:
    Path('./logs').mkdir(exist_ok=True)

    app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)

    origins = get_config().CORS_ORIGINS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(main.router, prefix='/api')

    return app


app = create_app()
if __name__ == '__main__':
    uvicorn.run(app, log_config=LOGGING_CONFIG)
