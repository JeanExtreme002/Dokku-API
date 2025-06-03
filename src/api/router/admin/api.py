import os
import signal

from fastapi import APIRouter, FastAPI, status
from fastapi.responses import JSONResponse

from src.api.models import DATABASE_URL
from src.config import Config


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/config", response_description="Return env variables of API server")
    async def get_config():
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "workers_count": Config.WORKERS_COUNT,
                "max_connections_per_request": Config.MAX_CONNECTIONS_PER_REQUEST,
                "reload": Config.RELOAD,
                "log_level": Config.LOG_LEVEL,
                "api_key": Config.API_KEY,
                "api_name": Config.API_NAME,
                "api_version_number": Config.API_VERSION_NUMBER,
                "volume_dir": Config.VOLUME_DIR,
                "ssh_server": {
                    "hostname": Config.SSH_SERVER.SSH_HOSTNAME,
                    "port": Config.SSH_SERVER.SSH_PORT,
                    "key_path": Config.SSH_SERVER.SSH_KEY_PATH,
                },
                "database": {
                    "host": Config.DATABASE.HOST,
                    "port": Config.DATABASE.PORT,
                    "db_name": Config.DATABASE.DB_NAME,
                    "user": Config.DATABASE.DB_USER,
                    "password": Config.DATABASE.DB_PASSWORD,
                    "url": DATABASE_URL,
                },
                "available_databases": Config.AVAILABLE_DATABASES,
            },
        )

    @router.post("/shutdown", response_description="Shutdown the API server")
    async def shutdown():
        os.kill(os.getpid(), signal.SIGTERM)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Server is shutting down"},
        )

    return router
