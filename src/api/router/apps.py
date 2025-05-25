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

    @router.post(
        "/deployment_token/{app_name}",
        response_description="Return the deployment token of an application",
    )
    async def get_deployment_token(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.get_deployment_token(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/logs/{app_name}", response_description="Return the logs of an application"
    )
    async def get_logs(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.get_logs(request.state.session_user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/network/{app_name}",
        response_description="Return the network of an application",
    )
    async def get_network(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.get_network(request.state.session_user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    return router
