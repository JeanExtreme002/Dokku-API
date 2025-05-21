from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.openapi.models import APIKey
from fastapi.responses import JSONResponse

from src.api.commands import DomainsCommands
from src.api.tools import validate_api_key


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
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = DomainsCommands.set_domain(app_name, domain_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.delete(
        "/{app_name}/{domain_name}",
        response_description="Remove a domain from an application",
    )
    async def domain_remove(
        request: Request,
        app_name: str,
        domain_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = DomainsCommands.remove_domain(app_name, domain_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    return router
