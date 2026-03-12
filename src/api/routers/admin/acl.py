from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services import ACLService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/run/",
        response_description="Run a dokku-acl command",
    )
    async def run_acl_command(
        request: Request,
        command: str,
    ):
        success, result = await ACLService.run_acl_command(command)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    return router
