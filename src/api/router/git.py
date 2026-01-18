from typing import Optional

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services import GitService
from src.api.tools.resource import check_shared_app


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/{app_name}/info/",
        response_description="Return information about the deployment of an application",
    )
    async def get_info(
        request: Request,
        app_name: str,
        shared_by: Optional[str] = None,
    ):
        session_user = request.state.session_user

        if shared_by is not None:
            session_user = await check_shared_app(session_user, app_name, shared_by)

        success, result = await GitService.get_deployment_info(session_user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.put(
        "/{app_name}/",
        response_description="Deploy an application by repository URL",
    )
    async def deploy_app_by_url(
        request: Request,
        app_name: str,
        repo_url: str,
        branch: str = "main",
        shared_by: Optional[str] = None,
    ):
        session_user = request.state.session_user

        if shared_by is not None:
            session_user = await check_shared_app(session_user, app_name, shared_by)

        success, result = await GitService.deploy_application_by_url(
            session_user, app_name, repo_url, branch
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
