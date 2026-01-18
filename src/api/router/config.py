from typing import Optional

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services import ConfigService
from src.api.tools.resource import check_shared_app


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/{app_name}/",
        response_description="Return application configurations",
    )
    async def list_config(
        request: Request,
        app_name: str,
        shared_by: Optional[str] = None,
    ):
        session_user = request.state.session_user

        if shared_by is not None:
            session_user = await check_shared_app(session_user, app_name, shared_by)

        success, result = await ConfigService.list_config(session_user, app_name)

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
        shared_by: Optional[str] = None,
    ):
        session_user = request.state.session_user

        if shared_by is not None:
            session_user = await check_shared_app(session_user, app_name, shared_by)

        success, result = await ConfigService.get_config(session_user, app_name, key)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.put(
        "/{app_name}/{key}/",
        response_description="Set application configuration key (without restart)",
    )
    async def set_config(
        request: Request,
        app_name: str,
        key: str,
        value: str,
        shared_by: Optional[str] = None,
    ):
        session_user = request.state.session_user

        if shared_by is not None:
            session_user = await check_shared_app(session_user, app_name, shared_by)

        success, result = await ConfigService.set_config(
            session_user, app_name, key, value
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
        shared_by: Optional[str] = None,
    ):
        session_user = request.state.session_user

        if shared_by is not None:
            session_user = await check_shared_app(session_user, app_name, shared_by)

        success, result = await ConfigService.unset_config(session_user, app_name, key)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
