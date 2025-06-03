from abc import ABC
from typing import Any, Tuple

from fastapi import HTTPException

from src.api.models import App
from src.api.schemas import UserSchema
from src.api.tools.name import ResourceName
from src.api.tools.ssh import run_command


class LetsencryptService(ABC):

    @staticmethod
    async def enable_letsencrypt(
        session_user: UserSchema, app_name: str
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        success, message = await run_command(f"letsencrypt:enable {app_name}")

        if "retrieval failed" in message:
            return False, message

        return success, message

    @staticmethod
    async def disable_letsencrypt(
        session_user: UserSchema,
        app_name: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        return await run_command(f"letsencrypt:disable {app_name}")

    @staticmethod
    async def set_letsencrypt_email(email: str) -> Tuple[bool, Any]:
        return await run_command(f"config:set --global DOKKU_LETSENCRYPT_EMAIL={email}")

    @staticmethod
    async def enable_letsencrypt_auto_renewal() -> Tuple[bool, Any]:
        return await run_command("letsencrypt:cron-job --add")
