from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services import NetworkService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/list/", response_description="Return all networks")
    async def list_networks(request: Request):
        success, result = await NetworkService.list_networks(request.state.session_user)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post("/{network_name}/", response_description="Create a network")
    async def create_network(
        request: Request,
        network_name: str,
    ):
        success, result = await NetworkService.create_network(
            request.state.session_user, network_name
        )
        status_code = status.HTTP_201_CREATED

        if not success:
            status_code = status.HTTP_200_OK

        return JSONResponse(
            status_code=status_code,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.delete("/{network_name}/", response_description="Delete a network")
    async def delete_network(
        request: Request,
        network_name: str,
    ):
        success, result = await NetworkService.delete_network(
            request.state.session_user, network_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{network_name}/linked-apps/",
        response_description="Return all apps linked to a network",
    )
    async def get_linked_apps(
        request: Request,
        network_name: str,
    ):
        success, result = await NetworkService.get_linked_apps(
            request.state.session_user, network_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{network_name}/link/{app_name}/",
        response_description="Set network to app",
    )
    async def set_network_to_app(
        request: Request,
        network_name: str,
        app_name: str,
    ):
        success, result = await NetworkService.set_network_to_app(
            request.state.session_user, network_name, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.delete(
        "/{network_name}/link/{app_name}/",
        response_description="Unset network from app",
    )
    async def unset_network_from_app(
        request: Request,
        network_name: str,
        app_name: str,
    ):
        success, result = await NetworkService.unset_network_to_app(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
