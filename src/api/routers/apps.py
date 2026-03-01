import os
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import get_db_session
from src.api.services import AppService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/list/", response_description="Return all applications")
    async def list_apps(request: Request, return_info: bool = True):
        success, result = await AppService.list_apps(
            request.state.session_user, return_info
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/list-shared-apps/", response_description="Return all shared applications"
    )
    async def list_shared_apps(request: Request, return_info: bool = True):
        success, result = await AppService.list_shared_apps(
            request.state.session_user, return_info
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/sharing/",
        response_description="Returns all users with whom the application is being shared",
    )
    async def get_shared_app_users(
        request: Request,
        app_name: str,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        success, result = await AppService.get_shared_app_users(
            request.state.session_user,
            app_name,
            db_session,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/exec/",
        response_description="Execute a command into the application's container",
    )
    async def execute_command(
        request: Request,
        app_name: str,
        command: str,
        container_type: Optional[str] = "web",
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.execute_command(
            request.state.session_user, app_name, container_type, command, shared_by
        )

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
        db_session: AsyncSession = Depends(get_db_session),
    ):
        success, result = await AppService.create_app(
            request.state.session_user,
            app_name,
            db_session,
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

    @router.post(
        "/{app_name}/clone/{existing_app_name}/",
        response_description="Clone an application",
    )
    async def clone_app(
        request: Request,
        app_name: str,
        existing_app_name: str,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        success, result = await AppService.create_app(
            request.state.session_user,
            app_name,
            db_session,
            existing_app_name,
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

    @router.post(
        "/{app_name}/exists/",
        response_description="Check if an application exists",
    )
    async def app_exists(
        request: Request,
        app_name: str,
    ):
        success, result = await AppService.app_exists(
            request.state.session_user, app_name
        )
        status_code = status.HTTP_200_OK if success else status.HTTP_404_NOT_FOUND

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
        db_session: AsyncSession = Depends(get_db_session),
    ):
        success, result = await AppService.delete_app(
            request.state.session_user, app_name, db_session
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
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.get_app_url(
            request.state.session_user, app_name, shared_by
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/rename/{new_app_name}/",
        response_description="Rename the application",
    )
    async def rename_app(
        request: Request,
        app_name: str,
        new_app_name: str,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        success, result = await AppService.rename_app(
            request.state.session_user,
            app_name,
            new_app_name,
            db_session,
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
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.get_app_info(
            request.state.session_user, app_name, shared_by
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
        db_session: AsyncSession = Depends(get_db_session),
    ):
        success, result = await AppService.get_deployment_token(
            request.state.session_user, app_name, db_session
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
        n_lines: int = 2000,
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.get_logs(
            request.state.session_user, app_name, n_lines, shared_by
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
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.start_app(
            request.state.session_user, app_name, shared_by
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
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.stop_app(
            request.state.session_user, app_name, shared_by
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
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.restart_app(
            request.state.session_user, app_name, shared_by
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
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.rebuild_app(
            request.state.session_user, app_name, shared_by
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
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.get_builder(
            request.state.session_user, app_name, shared_by
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
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.set_builder(
            request.state.session_user, app_name, builder, shared_by
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
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.get_linked_databases(
            request.state.session_user, app_name, shared_by
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
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.get_network(
            request.state.session_user, app_name, shared_by
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
        use_proxy: bool = False,
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.list_port_mappings(
            request.state.session_user, app_name, use_proxy, shared_by
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
        use_proxy: bool = False,
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.add_port_mapping(
            request.state.session_user,
            app_name,
            origin_port,
            dest_port,
            protocol,
            use_proxy,
            shared_by,
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
        use_proxy: bool = False,
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.remove_port_mapping(
            request.state.session_user,
            app_name,
            origin_port,
            dest_port,
            protocol,
            use_proxy,
            shared_by,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{app_name}/download/",
        response_description="Download a file from the application's container",
    )
    async def download_file(
        request: Request,
        app_name: str,
        filename: str,
        shared_by: Optional[str] = None,
    ):
        success, result = await AppService.download_file(
            request.state.session_user, app_name, filename, shared_by
        )

        if not success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": success,
                    "result": result,
                },
            )

        return Response(
            content=result,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={os.path.basename(filename)}",
            },
        )

    @router.post(
        "/{app_name}/share/{target_email}/",
        response_description="Share app with a third-party user",
    )
    async def share_app(
        request: Request,
        app_name: str,
        target_email: str,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        success, result = await AppService.share_app(
            request.state.session_user, app_name, target_email, db_session
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.delete(
        "/{app_name}/share/{target_email}/",
        response_description="Unshare app with a third-party user",
    )
    async def unshare_app(
        request: Request,
        app_name: str,
        target_email: str,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        success, result = await AppService.unshare_app(
            request.state.session_user, app_name, target_email, db_session
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
