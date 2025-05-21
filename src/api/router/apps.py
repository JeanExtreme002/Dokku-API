from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.openapi.models import APIKey
from fastapi.responses import JSONResponse

from src.api.commands import AppsCommands
from src.api.tools import validate_api_key


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_description="Return all applications")
    async def list_apps(
        request: Request, api_key: APIKey = Depends(validate_api_key)
    ):
        success, result = AppsCommands.list_apps()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.post("/{app_name}", response_description="Create an application")
    async def create_app(
        request: Request,
        app_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = AppsCommands.create_app(app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.delete("/{app_name}", response_description="Delete an application")
    async def delete_app(
        request: Request,
        app_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = AppsCommands.delete_app(app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    return router
