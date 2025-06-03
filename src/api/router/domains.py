from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services import DomainService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/{domain_name}/{app_name}",
        response_description="Set a domain for an application",
    )
    async def set_domain(
        request: Request,
        app_name: str,
        domain_name: str,
    ):
        success, result = await DomainService.set_domain(
            request.state.session_user, app_name, domain_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.delete(
        "/{domain_name}/{app_name}",
        response_description="Remove a domain from an application",
    )
    async def remove_domain(
        request: Request,
        app_name: str,
        domain_name: str,
    ):
        success, result = await DomainService.remove_domain(
            request.state.session_user, app_name, domain_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
