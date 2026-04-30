from typing import Literal, Optional

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services.nginx import NginxService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/{app_name}/logs/",
        response_description="Get nginx logs for an application",
    )
    async def get_logs(
        request: Request,
        app_name: str,
        type: Literal["access", "error"] = "access",
        shared_by: Optional[str] = None,
    ):
        if type == "access":
            success, result = await NginxService.get_access_logs(
                request.state.session_user, app_name, shared_by
            )
        else:
            success, result = await NginxService.get_error_logs(
                request.state.session_user, app_name, shared_by
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
