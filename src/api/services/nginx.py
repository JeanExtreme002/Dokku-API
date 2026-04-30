from abc import ABC
from typing import Any, Optional, Tuple

from fastapi import HTTPException

from src.api.schemas import UserSchema
from src.api.tools.resource import ResourceName, check_shared_app
from src.api.tools.ssh import run_command


class NginxService(ABC):

    @staticmethod
    async def get_access_logs(
        session_user: UserSchema,
        app_name: str,
        shared_by: Optional[str] = None,
    ) -> Tuple[bool, Any]:
        session_user = await check_shared_app(session_user, app_name, shared_by)
        app_name = ResourceName(session_user, app_name).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f"nginx:access-logs {app_name}")

    @staticmethod
    async def get_error_logs(
        session_user: UserSchema,
        app_name: str,
        shared_by: Optional[str] = None,
    ) -> Tuple[bool, Any]:
        session_user = await check_shared_app(session_user, app_name, shared_by)
        app_name = ResourceName(session_user, app_name).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f"nginx:error-logs {app_name}")
