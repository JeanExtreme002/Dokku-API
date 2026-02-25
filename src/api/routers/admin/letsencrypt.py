from fastapi import APIRouter, FastAPI, status
from fastapi.responses import JSONResponse

from src.api.services import LetsencryptService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/{email}/", response_description="Set a email for LetsEncrypt")
    async def set_letsencrypt_email(email: str):
        success, result = await LetsencryptService.set_letsencrypt_email(email)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.post(
        "/enable-auto-renewal/",
        response_description="Enable automatic LetsEncrypt renewal",
    )
    async def enable_letsencrypt_auto_renewal():
        success, result = await LetsencryptService.enable_letsencrypt_auto_renewal()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    return router
