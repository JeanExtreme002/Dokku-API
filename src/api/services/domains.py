from abc import ABC
from typing import Any, Tuple

from fastapi import HTTPException

from src.api.models import App
from src.api.schemas import UserSchema
from src.api.tools.name import ResourceName
from src.api.tools.ssh import run_command


class DomainService(ABC):

    @staticmethod
    async def set_domain(
        session_user: UserSchema,
        app_name: str,
        domain: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        return await run_command(f"domains:set {app_name} {domain}")

    @staticmethod
    async def remove_domain(
        session_user: UserSchema,
        app_name: str,
        domain: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        return await run_command(f"domains:remove {app_name} {domain}")
