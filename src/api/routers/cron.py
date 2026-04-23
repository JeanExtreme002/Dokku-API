from typing import Optional

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services.cron import CronService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/{app_name}/list/",
        response_description="List cron jobs for an application",
    )
    async def list_cron(
        request: Request,
        app_name: str,
        shared_by: Optional[str] = None,
    ):
        success, result = await CronService.list_cron(
            request.state.session_user, app_name, shared_by
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/run/",
        response_description="Run a cron job for an application",
    )
    async def run_cron(
        request: Request,
        app_name: str,
        cron_id: str,
        shared_by: Optional[str] = None,
    ):
        success, result = await CronService.run_cron(
            request.state.session_user, app_name, cron_id, shared_by
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
