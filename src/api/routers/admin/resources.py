from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import App, Network, Service, get_db_session, get_resources


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/apps/", response_description="Get apps from database")
    async def get_apps(
        request: Request,
        offset: int = 0,
        limit: int = 20,
        asc_created_at: bool = False,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        apps = await get_resources(
            App,
            offset,
            limit,
            db_session=db_session,
            asc_created_at=asc_created_at,
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=apps)

    @router.post("/services/", response_description="Get services from database")
    async def get_services(
        request: Request,
        offset: int = 0,
        limit: int = 20,
        asc_created_at: bool = False,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        services = await get_resources(
            Service,
            offset,
            limit,
            db_session=db_session,
            asc_created_at=asc_created_at,
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=services)

    @router.post("/networks/", response_description="Get networks from database")
    async def get_networks(
        request: Request,
        offset: int = 0,
        limit: int = 20,
        asc_created_at: bool = False,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        networks = await get_resources(
            Network,
            offset,
            limit,
            db_session=db_session,
            asc_created_at=asc_created_at,
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=networks)

    return router
