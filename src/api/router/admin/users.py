from typing import Optional

from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.api.models import create_user, delete_user, get_user, get_users, update_user


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/list", response_description="Get all users")
    async def get_all_users(request: Request):
        return JSONResponse(status_code=status.HTTP_200_OK, content=get_users())

    @router.post("/", response_description="Create a new user")
    async def create_new_user(request: Request, email: str, access_token: str):
        create_user(email, access_token)
        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.delete("/", response_description="Delete user")
    async def delete_user_from_database(request: Request, email: str):
        delete_user(email)
        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.put("/email", response_description="Update the user's email")
    async def update_email(request: Request, email: str, new_email: str):
        user = get_user(email)
        user.email = new_email

        update_user(email, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.put("/accessToken", response_description="Update the user's access token")
    async def update_access_token(
        request: Request,
        email: str,
        new_access_token: str,
        create_if_not_exists: bool = False,
    ):
        user = None

        try:
            user = get_user(email)
        except HTTPException as error:
            if error.status_code == 404 and not create_if_not_exists:
                raise error
            create_user(email, new_access_token)
            user = get_user(email)

        user.access_token = new_access_token
        update_user(email, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.put("/quota", response_description="Update the user's quotas")
    async def update_quota(
        request: Request,
        email: str,
        apps_quota: Optional[int] = None,
        services_quota: Optional[int] = None,
        networks_quota: Optional[int] = None,
        storage_quota: Optional[int] = None,
    ):
        user = get_user(email)

        user.apps_quota = apps_quota if apps_quota is not None else user.apps_quota
        user.services_quota = (
            services_quota if services_quota is not None else user.services_quota
        )
        user.networks_quota = (
            networks_quota if networks_quota is not None else user.networks_quota
        )
        user.storage_quota = (
            storage_quota if storage_quota is not None else user.storage_quota
        )

        update_user(email, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.put("/admin", response_description="Set a the user as admin or not")
    async def set_admin(request: Request, email: str, is_admin: bool):
        user = get_user(email)
        user.is_admin = is_admin

        update_user(email, user)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    return router
