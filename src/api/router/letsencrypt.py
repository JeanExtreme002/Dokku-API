from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.commands import LetsencryptCommands


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/app/{app_name}",
        response_description="Enable LetsEncrypt for an application",
    )
    async def letsencrypt_enable_app(
        request: Request,
        app_name: str,
    ):
        success, result = LetsencryptCommands.enable_letsencrypt(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.delete(
        "/app/{app_name}",
        response_description="Disable LetsEncrypt for an application",
    )
    async def letsencrypt_disable_app(
        request: Request,
        app_name: str,
    ):
        success, result = LetsencryptCommands.disable_letsencrypt(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    return router
