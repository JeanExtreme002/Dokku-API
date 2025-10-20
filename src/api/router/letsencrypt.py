from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services import LetsencryptService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/{app_name}/",
        response_description="Enable LetsEncrypt for an application",
    )
    async def enable_letsencrypt_app(
        request: Request,
        app_name: str,
    ):
        success, result = await LetsencryptService.enable_letsencrypt(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.delete(
        "/{app_name}/",
        response_description="Disable LetsEncrypt for an application",
    )
    async def disable_letsencrypt_app(
        request: Request,
        app_name: str,
    ):
        success, result = await LetsencryptService.disable_letsencrypt(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
