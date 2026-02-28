import datetime
import os
import tempfile
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import (
    App,
    Network,
    Service,
    create_take_over_access_token,
    create_user,
    delete_user,
    get_db_session,
    get_user,
    get_users,
    update_user,
)
from src.api.services import AppService, DatabaseService, NetworkService
from src.api.tools import hash_access_token
from src.api.tools.resource import ResourceName
from src.api.tools.ssh import run_command_as_root


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post("/list/", response_description="Get all users")
    async def get_all_users(
        request: Request,
        only_admin: bool = False,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        users = await get_users(db_session, only_admin)
        return JSONResponse(status_code=status.HTTP_200_OK, content=users)

    @router.post("/{email}/", response_description="Create a new user")
    async def create_new_user(
        request: Request,
        email: str,
        access_token: str,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        await create_user(email, access_token, db_session)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={})

    @router.post("/{email}/take-over/", response_description="Take over an user")
    async def take_over_user(
        request: Request,
        email: str,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        access_token = await create_take_over_access_token(email, db_session)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"access_token": access_token}
        )

    @router.delete("/{email}/", response_description="Delete user")
    async def delete_user_from_database(
        request: Request,
        email: str,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        user = await get_user(email, db_session)

        for app_name in user.apps:
            app_name = str(ResourceName(user, app_name, App, from_system=True))
            await AppService.delete_app(user, app_name, db_session)

        for service_name in user.services:
            plugin_name, database_name = service_name.split(":", maxsplit=1)
            database_name = str(
                ResourceName(user, database_name, Service, from_system=True)
            )
            await DatabaseService.delete_database(
                user, plugin_name, database_name, db_session
            )

        for network_name in user.networks:
            network_name = str(
                ResourceName(user, network_name, Network, from_system=True)
            )
            await NetworkService.delete_network(user, network_name, db_session)

        await delete_user(email, db_session)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.put("/{email}/email/", response_description="Update the user's email")
    async def update_email(
        request: Request,
        email: str,
        new_email: str,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        user = await get_user(email, db_session)
        user.email = new_email

        try:
            await get_user(new_email, db_session)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )
        except HTTPException as error:
            if error.status_code != 404:
                raise error

        await update_user(email, user, db_session)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.put(
        "/{email}/access-token/", response_description="Update the user's access token"
    )
    async def update_access_token(
        request: Request,
        email: str,
        new_access_token: str,
        create_if_not_exists: bool = False,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        user = None

        try:
            user = await get_user(email, db_session)
        except HTTPException as error:
            if error.status_code == 404 and not create_if_not_exists:
                raise error
            await create_user(email, new_access_token, db_session)
            user = await get_user(email, db_session)

        new_access_token_expiration = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(days=7)

        new_access_token = hash_access_token(new_access_token)
        user.access_token = new_access_token
        user.access_token_expiration = new_access_token_expiration

        await update_user(email, user, db_session)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.post("/{email}/quota/", response_description="Get user's quota information")
    async def get_quota(
        request: Request,
        email: str,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        user = await get_user(email, db_session)

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
        db_session: AsyncSession = Depends(get_db_session),
    ):
        user = await get_user(email, db_session)

        user.apps_quota = apps_quota if apps_quota is not None else user.apps_quota
        user.services_quota = (
            services_quota if services_quota is not None else user.services_quota
        )
        user.networks_quota = (
            networks_quota if networks_quota is not None else user.networks_quota
        )

        await update_user(email, user, db_session)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.post(
        "/{email}/admin/", response_description="Check if the user is admin or not"
    )
    async def is_admin(
        request: Request,
        email: str,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        user = await get_user(email, db_session)

        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": user.is_admin}
        )

    @router.put("/{email}/admin/", response_description="Set the user as admin or not")
    async def set_admin(
        request: Request,
        email: str,
        is_admin: bool,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        user = await get_user(email, db_session)
        user.is_admin = is_admin

        await update_user(email, user, db_session)

        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    @router.post("/{email}/ssh-key/", response_description="Set a SSH key for the user")
    async def set_ssh_key(
        request: Request,
        email: str,
        public_ssh_key_file: UploadFile = File(...),
        db_session: AsyncSession = Depends(get_db_session),
    ):
        await get_user(email, db_session)

        with tempfile.NamedTemporaryFile(
            mode="w+b", delete=False, suffix=".pub"
        ) as temp_file:
            content = await public_ssh_key_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            command = f"ssh-keys:add {email} {temp_file_path}"
            success, message = await run_command_as_root(command)
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": message,
                "success": success,
            },
        )

    return router
