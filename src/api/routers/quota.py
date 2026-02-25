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

    @router.post("/used/", response_description="Get user's used resources")
    async def get_used(request: Request):
        user = request.state.session_user

        used = {
            "apps_used": len(user.apps) if user.apps else 0,
            "services_used": len(user.services) if user.services else 0,
            "networks_used": len(user.networks) if user.networks else 0,
        }

        return JSONResponse(status_code=status.HTTP_200_OK, content=used)

    return router
