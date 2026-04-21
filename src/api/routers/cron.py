from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services.cron import CronService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/list/",
        response_description="List cron jobs for an application",
    )
    async def list_cron(
        request: Request,
        app_name: str,
    ):
        success, result = await CronService.list_cron(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/run/",
        response_description="Run a cron job for an application",
    )
    async def run_cron(
        request: Request,
        app_name: str,
        cron_id: str,
    ):
        success, result = await CronService.run_cron(
            request.state.session_user, app_name, cron_id
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
