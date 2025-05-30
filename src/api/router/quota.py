from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/", response_description="Get user's quota")
    async def get_quota(request: Request):
        user = request.state.session_user

        quota = {
            "apps_quota": user.apps_quota,
            "services_quota": user.services_quota,
            "networks_quota": user.networks_quota,
        }

        return JSONResponse(status_code=status.HTTP_200_OK, content=quota)

    return router
