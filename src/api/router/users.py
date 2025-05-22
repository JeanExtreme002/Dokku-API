from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.models import create_user


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/", response_description="Create a new user")
    async def create_new_user(request: Request, email: str, access_token: str):
        create_user(email, access_token)
        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    return router
