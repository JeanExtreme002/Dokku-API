from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.models import get_user
from src.api.services import AppService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/{email}/set-owner/{app_name}",
        response_description="Set a user as owner of an existing app",
    )
    async def set_owner(request: Request, email: str, app_name: str):
        user = await get_user(email)
        await AppService.set_owner(user, app_name)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.delete(
        "/{email}/set-owner/{app_name}", response_description="Unset owner from an app"
    )
    async def unset_owner(request: Request, email: str, app_name: str):
        user = await get_user(email)
        await AppService.unset_owner(user, app_name)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.post(
        "/storage/{email}/{app_name}/", response_description="List storage of an app"
    )
    async def list_storage(email: str, app_name: str):
        user = await get_user(email)

        success, result = await AppService.list_storage(user, app_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.put(
        "/storage/{email}/{app_name}/", response_description="Mount storage for app"
    )
    async def mount_storage(email: str, app_name: str, directory: str = "/app/storage"):
        user = await get_user(email)

        success, result = await AppService.mount_storage(user, app_name, directory)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    @router.delete(
        "/storage/{email}/{app_name}/", response_description="Unmount storage for app"
    )
    async def unmount_storage(
        email: str, app_name: str, directory: str = "/app/storage"
    ):
        user = await get_user(email)

        success, result = await AppService.unmount_storage(user, app_name, directory)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": success, "result": result},
        )

    return router
