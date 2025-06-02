from fastapi import APIRouter, FastAPI, status
from fastapi.responses import JSONResponse

from src.api.commands import AppsCommands
from src.api.models import get_user


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/storage/{email}/{app_name}", response_description="Mount storage for app"
    )
    async def mount_storage(email: str, app_name: str):
        user = await get_user(email)

        success, result = await AppsCommands.mount_storage(user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.delete(
        "/storage/{email}/{app_name}", response_description="Unmount storage for app"
    )
    async def unmount_storage(email: str, app_name: str):
        user = await get_user(email)

        success, result = await AppsCommands.unmount_storage(user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    return router
