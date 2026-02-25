from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services import DatabaseService, get_dokku_version
from src.config import Config


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_description="Return details about the API")
    async def get_details(request: Request):
        success, dokku_version = await get_dokku_version()

        result = {
            "app_name": Config.API_NAME,
            "version": Config.API_VERSION_NUMBER,
            "dokku_status": success,
            "dokku_version": dokku_version if success else None,
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    @router.get("/list-databases/", response_description="List available databases")
    async def list_available_databases(request: Request):
        success, result = await DatabaseService.list_available_databases()

        result = {
            "success": success,
            "result": result,
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    return router
