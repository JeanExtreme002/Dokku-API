from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.commands import DomainsCommands


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/{app_name}/{domain_name}",
        response_description="Set a domain for an application",
    )
    async def domain_set(
        request: Request,
        app_name: str,
        domain_name: str,
    ):
        success, result = DomainsCommands.set_domain(
            request.state.session_user, app_name, domain_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.delete(
        "/{app_name}/{domain_name}",
        response_description="Remove a domain from an application",
    )
    async def domain_remove(
        request: Request,
        app_name: str,
        domain_name: str,
    ):
        success, result = DomainsCommands.remove_domain(
            request.state.session_user, app_name, domain_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    return router
