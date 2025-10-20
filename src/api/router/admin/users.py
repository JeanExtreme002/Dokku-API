from typing import Optional

from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.api.models import (
    create_take_over_access_token,
    create_user,
    delete_user,
    get_user,
    get_users,
    update_user,
)
from src.api.services import AppService, DatabaseService
from src.api.tools import hash_access_token


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/list/", response_description="Get all users")
    async def get_all_users(request: Request):
        users = await get_users()
        return JSONResponse(status_code=status.HTTP_200_OK, content=users)

    @router.post("/{email}/", response_description="Create a new user")
    async def create_new_user(request: Request, email: str, access_token: str):
        await create_user(email, access_token)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={})

    @router.post("/{email}/take-over/", response_description="Take over an user")
    async def take_over_user(request: Request, email: str):
        access_token = await create_take_over_access_token(email)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"access_token": access_token}
        )

    @router.delete("/{email}/", response_description="Delete user")
    async def delete_user_from_database(request: Request, email: str):
        user = await get_user(email)

        for app_name in user.apps:
            await AppService.delete_app(user, app_name)

        for service_name in user.services:
            plugin_name, database_name = service_name.split(":", maxsplit=1)
            await DatabaseService.delete_database(user, plugin_name, database_name)

        await delete_user(email)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.put("/{email}/email/", response_description="Update the user's email")
    async def update_email(request: Request, email: str, new_email: str):
        user = await get_user(email)
        user.email = new_email

        try:
            await get_user(new_email)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )
        except HTTPException as error:
            if error.status_code != 404:
                raise error

        await update_user(email, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.put(
        "/{email}/access-token/", response_description="Update the user's access token"
    )
    async def update_access_token(
        request: Request,
        email: str,
        new_access_token: str,
        create_if_not_exists: bool = False,
    ):
        user = None

        try:
            user = await get_user(email)
        except HTTPException as error:
            if error.status_code == 404 and not create_if_not_exists:
                raise error
            await create_user(email, new_access_token)
            user = await get_user(email)

        new_access_token = hash_access_token(new_access_token)
        user.access_token = new_access_token
        await update_user(email, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.post("/{email}/quota/", response_description="Get user's quota information")
    async def get_quota(
        request: Request,
        email: str,
    ):
        user = await get_user(email)

        quota = {
            "apps_quota": user.apps_quota,
            "services_quota": user.services_quota,
            "networks_quota": user.networks_quota,
        }

        return JSONResponse(status_code=status.HTTP_200_OK, content=quota)

    @router.put("/{email}/quota/", response_description="Update the user's quotas")
    async def update_quota(
        request: Request,
        email: str,
        apps_quota: Optional[int] = None,
        services_quota: Optional[int] = None,
        networks_quota: Optional[int] = None,
    ):
        user = await get_user(email)

        user.apps_quota = apps_quota if apps_quota is not None else user.apps_quota
        user.services_quota = (
            services_quota if services_quota is not None else user.services_quota
        )
        user.networks_quota = (
            networks_quota if networks_quota is not None else user.networks_quota
        )

        await update_user(email, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.post(
        "/{email}/admin/", response_description="Check if the user is admin or not"
    )
    async def is_admin(request: Request, email: str):
        user = await get_user(email)

        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": user.is_admin}
        )

    @router.put(
        "/{email}/admin/", response_description="Set a the user as admin or not"
    )
    async def set_admin(request: Request, email: str, is_admin: bool):
        user = await get_user(email)
        user.is_admin = is_admin

        await update_user(email, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    return router
