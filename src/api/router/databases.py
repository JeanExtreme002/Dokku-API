from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.openapi.models import APIKey
from fastapi.responses import JSONResponse

from src.api.commands import DatabasesCommands
from src.api.tools import validate_api_key


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.get("/{plugin_name}", response_description="Return all databases")
    async def list_databases(
        request: Request,
        plugin_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = DatabasesCommands.list_databases(plugin_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.get(
        "/{plugin_name}/{database_name}",
        response_description="Check if a database exists",
    )
    async def database_exists(
        request: Request,
        plugin_name: str,
        database_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = DatabasesCommands.database_exists(
            plugin_name, database_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.post(
        "/{plugin_name}/{database_name}",
        response_description="Create a database",
    )
    async def create_database(
        request: Request,
        plugin_name: str,
        database_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = DatabasesCommands.create_database(
            plugin_name, database_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.delete(
        "/{plugin_name}/{database_name}",
        response_description="Delete a database",
    )
    async def delete_database(
        request: Request,
        plugin_name: str,
        database_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = DatabasesCommands.delete_database(
            plugin_name, database_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.get(
        "/links/{plugin_name}/{database_name}",
        response_description="List linked apps",
    )
    async def database_linked_apps(
        request: Request,
        plugin_name: str,
        database_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = DatabasesCommands.database_linked_apps(
            plugin_name, database_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.post(
        "/links/{plugin_name}/{database_name}/{app_name}",
        response_description="Link a database to an app",
    )
    async def link_database(
        request: Request,
        plugin_name: str,
        database_name: str,
        app_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = DatabasesCommands.link_database(
            plugin_name, database_name, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.delete(
        "/links/{plugin_name}/{database_name}/{app_name}",
        response_description="Unlink a database from an app",
    )
    async def unlink_database(
        request: Request,
        plugin_name: str,
        database_name: str,
        app_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = DatabasesCommands.unlink_database(
            plugin_name, database_name, app_name
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    return router
