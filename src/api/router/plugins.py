from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.openapi.models import APIKey
from fastapi.responses import JSONResponse

from src.api.commands import PluginsCommands
from src.api.tools import validate_api_key


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_description="Return all plugins")
    async def list_plugins(
        request: Request, api_key: APIKey = Depends(validate_api_key)
    ):
        success, result = PluginsCommands.list_plugins()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.get(
        "/{plugin_name}", response_description="Check if plugin is installed"
    )
    async def plugin_installed(
        request: Request,
        plugin_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = PluginsCommands.is_plugin_installed(plugin_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.post("/{plugin_name}", response_description="Install plugin")
    async def install_plugin(
        request: Request,
        plugin_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = PluginsCommands.install_plugin(plugin_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.delete("/{plugin_name}", response_description="Uninstall plugin")
    async def uninstall_plugin(
        request: Request,
        plugin_name: str,
        api_key: APIKey = Depends(validate_api_key),
    ):
        success, result = PluginsCommands.uninstall_plugin(plugin_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    return router
