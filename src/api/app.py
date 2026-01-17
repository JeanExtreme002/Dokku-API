import logging
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.middlewares import SessionUserMiddleware
from src.api.router import get_router
from src.api.services import AppService
from src.config import Config

APP_ROOT = Path(__file__).parent

scheduler = AsyncIOScheduler()


async def sync_database_with_dokku():
    await AppService.sync_database()


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of the application.
    """
    logging.basicConfig(level=Config.LOG_LEVEL.upper())

    _app = FastAPI(
        title="Dokku API",
        default_response_class=JSONResponse,
        version=Config.API_VERSION_NUMBER,
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.add_middleware(SessionUserMiddleware)

    _app.include_router(get_router(_app))

    @_app.on_event("startup")
    async def startup():
        scheduler.start()
        scheduler.add_job(
            sync_database_with_dokku,
            trigger=IntervalTrigger(hours=1),
            id="sync_db_w_dokku_task",
            replace_existing=True,
            next_run_time=datetime.now(),
            max_instances=1,
            coalesce=True,
        )

    return _app
