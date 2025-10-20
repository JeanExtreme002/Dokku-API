from fastapi import APIRouter, FastAPI, status
from fastapi.responses import JSONResponse

from src.api.services import PluginService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/list/", response_description="Return all plugins")
    async def list_plugins():
        success, result = await PluginService.list_plugins()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.post("/{plugin_name}/", response_description="Install plugin")
    async def install_plugin(plugin_name: str, plugin_url: str):
        success, result = await PluginService.install_plugin(plugin_url, plugin_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.delete("/{plugin_name}/", response_description="Uninstall plugin")
    async def uninstall_plugin(plugin_name: str):
        success, result = await PluginService.uninstall_plugin(plugin_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.post(
        "/check/{plugin_name}/",
        response_description="Check if plugin is installed",
    )
    async def is_plugin_installed(plugin_name: str):
        success, result = await PluginService.is_plugin_installed(plugin_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    return router
