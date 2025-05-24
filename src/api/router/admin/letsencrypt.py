from fastapi import APIRouter, FastAPI, status
from fastapi.responses import JSONResponse

from src.api.commands import LetsencryptCommands


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/{mail}", response_description="Set a email for LetsEncrypt")
    async def letsencrypt_set_mail(email: str):
        success, result = LetsencryptCommands.set_letsencrypt_mail(email)

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
    async def letsencrypt_enable_auto_renewal():
        success, result = LetsencryptCommands.enable_letsencrypt_auto_renewal()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    return router
