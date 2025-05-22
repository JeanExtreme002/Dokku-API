from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.models import get_user


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/", response_description="Get user's quota")
    async def get_quota(request: Request, email: str):
        user = get_user(email)

        quota = {
            "apps_quota": user.apps_quota,
            "services_quota": user.services_quota,
            "networks_quota": user.networks_quota,
            "storage_quota": user.storage_quota,
        }

        return JSONResponse(status_code=status.HTTP_200_OK, content=quota)

    return router
