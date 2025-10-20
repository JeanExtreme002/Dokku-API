from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services import ConfigService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/{app_name}/",
        response_description="Return application configurations",
    )
    async def list_config(
        request: Request,
        app_name: str,
    ):
        success, result = await ConfigService.list_config(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/{key}/",
        response_description="Return value of application configuration key",
    )
    async def get_config(
        request: Request,
        app_name: str,
        key: str,
    ):
        success, result = await ConfigService.get_config(
            request.state.session_user, app_name, key
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/{key}/{value}/",
        response_description="Set application configuration key (without restart)",
    )
    async def set_config(
        request: Request,
        app_name: str,
        key: str,
        value: str,
    ):
        success, result = await ConfigService.set_config(
            request.state.session_user, app_name, key, value
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.delete(
        "/{app_name}/{key}/",
        response_description="Unset application configuration key (without restart)",
    )
    async def unset_config(
        request: Request,
        app_name: str,
        key: str,
    ):
        success, result = await ConfigService.unset_config(
            request.state.session_user, app_name, key
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
