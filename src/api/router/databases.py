from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.services import DatabaseService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/list/", response_description="Return all databases")
    async def list_all_databases(request: Request):
        success, result = await DatabaseService.list_all_databases(
            request.state.session_user
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{plugin_name}/list/",
        response_description="Return all databases, given a plugin name",
    )
    async def list_databases(
        request: Request,
        plugin_name: str,
    ):
        success, result = await DatabaseService.list_databases(
            request.state.session_user, plugin_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{plugin_name}/{database_name}/",
        response_description="Create a database",
    )
    async def create_database(
        request: Request,
        plugin_name: str,
        database_name: str,
    ):
        success, result = await DatabaseService.create_database(
            request.state.session_user, plugin_name, database_name
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

    @router.delete(
        "/{plugin_name}/{database_name}/",
        response_description="Delete a database",
    )
    async def delete_database(
        request: Request,
        plugin_name: str,
        database_name: str,
    ):
        success, result = await DatabaseService.delete_database(
            request.state.session_user, plugin_name, database_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{plugin_name}/{database_name}/uri/",
        response_description="Get the URI of a database",
    )
    async def get_uri(
        request: Request,
        plugin_name: str,
        database_name: str,
    ):
        success, result = await DatabaseService.get_database_uri(
            request.state.session_user, plugin_name, database_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{plugin_name}/{database_name}/info/",
        response_description="Return information about a database",
    )
    async def get_database_information(
        request: Request,
        plugin_name: str,
        database_name: str,
    ):
        success, result = await DatabaseService.get_database_info(
            request.state.session_user, plugin_name, database_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{plugin_name}/{database_name}/linked-apps/",
        response_description="Return all apps linked to a database",
    )
    async def get_linked_apps(
        request: Request,
        plugin_name: str,
        database_name: str,
    ):
        success, result = await DatabaseService.get_linked_apps(
            request.state.session_user, plugin_name, database_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.post(
        "/{plugin_name}/{database_name}/link/{app_name}/",
        response_description="Link a database to an app",
    )
    async def link_database(
        request: Request,
        plugin_name: str,
        database_name: str,
        app_name: str,
    ):
        success, result = await DatabaseService.link_database(
            request.state.session_user, plugin_name, database_name, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    @router.delete(
        "/{plugin_name}/{database_name}/link/{app_name}/",
        response_description="Unlink a database from an app",
    )
    async def unlink_database(
        request: Request,
        plugin_name: str,
        database_name: str,
        app_name: str,
    ):
        success, result = await DatabaseService.unlink_database(
            request.state.session_user, plugin_name, database_name, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
