from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.commands import ConfigCommands


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/{app_name}", response_description="Return application configurations"
    )
    async def list_config(
        request: Request,
        app_name: str,
    ):
        success, result = ConfigCommands.list_config(app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/{app_name}/{key}/{value}",
        response_description="Set application configuration key (without restart)",
    )
    async def set_config(
        request: Request,
        app_name: str,
        key: str,
        value: str,
    ):
        success, result = ConfigCommands.set_config(app_name, key, value)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.delete(
        "/{app_name}/{key}",
        response_description="Unset application configuration key (without restart)",
    )
    async def unset_config(
        request: Request,
        app_name: str,
        key: str,
    ):
        success, result = ConfigCommands.unset_config(app_name, key)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/{app_name}/keys/apply/restart",
        response_description="Apply application configuration (with restart)",
    )
    async def apply_config(
        request: Request,
        app_name: str,
    ):
        success, result = ConfigCommands.apply_config(app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    return router
