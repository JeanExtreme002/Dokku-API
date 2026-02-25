from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services import DomainService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/{app_name}/{domain_name}/",
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

    @router.post(
        "/{app_name}/",
        response_description="Get domains info of an application",
    )
    async def get_domains_info(
        request: Request,
        app_name: str,
    ):
        success, result = await DomainService.get_domains_info(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.put(
        "/{app_name}/{domain_name}/",
        response_description="Add a domain for an application",
    )
    async def add_domain(
        request: Request,
        app_name: str,
        domain_name: str,
    ):
        success, result = await DomainService.add_domain(
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
        "/{app_name}/{domain_name}/",
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
