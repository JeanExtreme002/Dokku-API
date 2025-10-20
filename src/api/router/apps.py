from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services import AppService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/list/", response_description="Return all applications")
    async def list_apps(request: Request):
        success, result = await AppService.list_apps(request.state.session_user)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post("/{app_name}/", response_description="Create an application")
    async def create_app(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.create_app(
            request.state.session_user, app_name
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

    @router.delete("/{app_name}/", response_description="Delete an application")
    async def delete_app(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.delete_app(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/url/",
        response_description="Return the application URL",
    )
    async def get_app_url(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.get_app_url(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/info/",
        response_description="Return information about an application",
    )
    async def get_app_information(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.get_app_info(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/deployment-token/",
        response_description="Return the deployment token of an application",
    )
    async def get_deployment_token(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.get_deployment_token(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/logs/",
        response_description="Return the logs of an application",
    )
    async def get_logs(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.get_logs(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/start/",
        response_description="Start an application",
    )
    async def start_app(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.start_app(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/stop/",
        response_description="Stop an application",
    )
    async def stop_app(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.stop_app(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/restart/",
        response_description="Restart an application",
    )
    async def restart_app(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.restart_app(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/rebuild/",
        response_description="Rebuild an application",
    )
    async def rebuild_app(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.rebuild_app(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/builder/",
        response_description="Get builder information of an application",
    )
    async def get_builder_info(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.get_builder(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/builder/{builder}/",
        response_description="Set builder of an application",
    )
    async def set_builder_info(
        request: Request,
        app_name: str,
        builder: str,
    ):
        success, result = await AppService.set_builder(
            request.state.session_user, app_name, builder
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/databases/",
        response_description="Return all databases linked to an application",
    )
    async def get_linked_databases(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.get_linked_databases(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/network/",
        response_description="Return the network of an application",
    )
    async def get_network(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.get_network(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/ports/",
        response_description="Return all ports of an application",
    )
    async def list_port_mappings(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.list_port_mappings(
            request.state.session_user, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/ports/{protocol}/{origin_port}/{dest_port}/",
        response_description="Add a port mapping to an application",
    )
    async def add_port_mapping(
        request: Request,
        app_name: str,
        origin_port: int,
        dest_port: int,
        protocol: str = "http",
    ):
        success, result = await AppService.add_port_mapping(
            request.state.session_user, app_name, origin_port, dest_port, protocol
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.delete(
        "/{app_name}/ports/{protocol}/{origin_port}/{dest_port}/",
        response_description="Remove a port mapping from an application",
    )
    async def remove_port_mapping(
        request: Request,
        app_name: str,
        origin_port: int,
        dest_port: int,
        protocol: str = "http",
    ):
        success, result = await AppService.remove_port_mapping(
            request.state.session_user, app_name, origin_port, dest_port, protocol
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
