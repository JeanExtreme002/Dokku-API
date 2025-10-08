import re
from abc import ABC
from typing import Any, Dict, Tuple

from fastapi import HTTPException

from src.api.models import App
from src.api.schemas import UserSchema
from src.api.tools.name import ResourceName
from src.api.tools.ssh import run_command


def parse_env_vars(text: str) -> Dict:
    result = {}
    lines = text.strip().splitlines()

    for line in lines:
        if line.startswith("=====>"):
            continue

        match = re.match(r"^(.+?):\s+(.*)$", line)

        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            result[key] = value

    return result


class ConfigService(ABC):

    @staticmethod
    async def list_config(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        success, message = await run_command(f"config:show {app_name}")

        return success, parse_env_vars(message)

    @staticmethod
    async def get_config(
        session_user: UserSchema,
        app_name: str,
        key: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        return await run_command(f"config:get {app_name} {key}")

    @staticmethod
    async def set_config(
        session_user: UserSchema,
        app_name: str,
        key: str,
        value: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        return await run_command(f"config:set --no-restart {app_name} {key}={value}")

    @staticmethod
    async def unset_config(
        session_user: UserSchema,
        app_name: str,
        key: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        return await run_command(f"config:unset --no-restart {app_name} {key}")
