from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.commands import AppsCommands


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/list", response_description="Return all applications")
    async def list_apps(request: Request):
        success, result = AppsCommands.list_apps(request.state.session_user)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post("/{app_name}", response_description="Create an application")
    async def create_app(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.create_app(request.state.session_user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.delete("/{app_name}", response_description="Delete an application")
    async def delete_app(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.delete_app(request.state.session_user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/{app_name}/url",
        response_description="Return the application URL",
    )
    async def get_app_url(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.get_app_url(request.state.session_user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/{app_name}/info",
        response_description="Return information about an application",
    )
    async def get_app_information(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.get_app_info(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/{app_name}/deployment-token",
        response_description="Return the deployment token of an application",
    )
    async def get_deployment_token(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.get_deployment_token(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/{app_name}/logs", response_description="Return the logs of an application"
    )
    async def get_logs(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.get_logs(request.state.session_user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/{app_name}/databases",
        response_description="Return all databases linked to an application",
    )
    async def get_linked_databases(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.get_linked_databases(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/{app_name}/network",
        response_description="Return the network of an application",
    )
    async def get_network(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.get_network(request.state.session_user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/{app_name}/ports",
        response_description="Return all ports of an application",
    )
    async def list_port_mappings(
        request: Request,
        app_name: str,
    ):
        success, result = AppsCommands.list_port_mappings(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.post(
        "/{app_name}/ports/{protocol}/{origin_port}/{dest_port}",
        response_description="Add a port mapping to an application",
    )
    async def add_port_mapping(
        request: Request,
        app_name: str,
        origin_port: int,
        dest_port: int,
        protocol: str = "http",
    ):
        success, result = AppsCommands.add_port_mapping(
            request.state.session_user, app_name, origin_port, dest_port, protocol
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    @router.delete(
        "/{app_name}/ports/{protocol}/{origin_port}/{dest_port}",
        response_description="Remove a port mapping from an application",
    )
    async def remove_port_mapping(
        request: Request,
        app_name: str,
        origin_port: int,
        dest_port: int,
        protocol: str = "http",
    ):
        success, result = AppsCommands.remove_port_mapping(
            request.state.session_user, app_name, origin_port, dest_port, protocol
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result
            },
        )

    return router
