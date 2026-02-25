from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.models import App, Network, Service, get_resources


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/apps/", response_description="Get apps from database")
    async def get_apps(
        request: Request, offset: int = 0, limit: int = 20, asc_created_at: bool = False
    ):
        apps = await get_resources(App, offset, limit, asc_created_at)
        return JSONResponse(status_code=status.HTTP_200_OK, content=apps)

    @router.post("/services/", response_description="Get services from database")
    async def get_services(
        request: Request, offset: int = 0, limit: int = 20, asc_created_at: bool = False
    ):
        services = await get_resources(Service, offset, limit, asc_created_at)
        return JSONResponse(status_code=status.HTTP_200_OK, content=services)

    @router.post("/networks/", response_description="Get networks from database")
    async def get_networks(
        request: Request, offset: int = 0, limit: int = 20, asc_created_at: bool = False
    ):
        networks = await get_resources(Network, offset, limit, asc_created_at)
        return JSONResponse(status_code=status.HTTP_200_OK, content=networks)

    return router
