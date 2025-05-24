from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.commands import DatabasesCommands
from src.config import Config


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_description="Return details about the API")
    async def get_details(request: Request):
        result = {
            "app_name": Config.API_NAME,
            "version": Config.API_VERSION_NUMBER,
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    @router.get("/databases", response_description="List available databases")
    async def list_available_databases(request: Request):
        success, result = DatabasesCommands.list_available_databases()

        result = {
            "success": success,
            "result": result,
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    return router
