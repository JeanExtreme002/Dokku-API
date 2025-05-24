from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.commands import AppsCommands


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/", response_description="Return all applications")
    async def list_apps(request: Request):
        success, result = AppsCommands.list_apps(request.state.session_user)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post("/{app_name}", response_description="Create an application")
    async def create_app(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.create_app(request.state.session_user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.delete("/{app_name}", response_description="Delete an application")
    async def delete_app(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.delete_app(request.state.session_user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    return router
