from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.commands import NetworksCommands


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/", response_description="Return all networks")
    async def list_networks(request: Request):
        success, result = NetworksCommands.list_networks(request.state.session_user)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post("/{network_name}", response_description="Create a network")
    async def create_network(
        request: Request,
        network_name: str,
    ):
        success, result = NetworksCommands.create_network(
            request.state.session_user, network_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.delete("/{network_name}", response_description="Delete a network")
    async def delete_network(
        request: Request,
        network_name: str,
    ):
        success, result = NetworksCommands.delete_network(
            request.state.session_user, network_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/links/{network_name}",
        response_description="Return all apps linked to a network",
    )
    async def get_linked_apps(
        request: Request,
        network_name: str,
    ):
        success, result = NetworksCommands.get_linked_apps(
            request.state.session_user, network_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/set{network_name}/{app_name}", response_description="Set network to app"
    )
    async def set_network_to_app(
        request: Request,
        network_name: str,
        app_name: str,
    ):
        success, result = NetworksCommands.set_network_to_app(
            request.state.session_user, network_name, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    return router
