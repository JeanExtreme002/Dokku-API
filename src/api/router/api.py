from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.config import settings


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_description="Return details about the API")
    async def get_details(request: Request):
        result = {
            "app_name": settings.API_NAME,
            "version": settings.API_VERSION_NUMBER,
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    return router
