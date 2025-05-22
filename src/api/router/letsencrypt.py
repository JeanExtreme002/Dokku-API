from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.openapi.models import APIKey
from fastapi.responses import JSONResponse

from src.api.commands import LetsencryptCommands
from src.api.tools import validate_api_key


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/{mail}", response_description="Set a mail for LetsEncrypt")
    async def letsencrypt_set_mail(
        request: Request, mail: str, api_key: APIKey = Depends(validate_api_key)
    ):
        success, result = LetsencryptCommands.set_letsencrypt_mail(mail)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/app/{app_name}",
        response_description="Enable LetsEncrypt for an application",
    )
    async def letsencrypt_enable_app(
        request: Request,
        app_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = LetsencryptCommands.enable_letsencrypt(app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/enable/auto/renewal",
        response_description="Enable automatic LetsEncrypt renewal",
    )
    async def letsencrypt_enable_auto_renewal(
        request: Request, api_key: APIKey = Depends(validate_api_key)
    ):
        success, result = LetsencryptCommands.enable_letsencrypt_auto_renewal()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    return router
