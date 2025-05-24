import re
from abc import ABC
from typing import Any, Tuple

from fastapi import HTTPException

from src.api.models.schema import UserSchema
from src.api.tools.ssh import run_command


def parse_env_vars(text: str) -> dict:
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


class ConfigCommands(ABC):

    @staticmethod
    def list_config(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        success, message = run_command(f"config:show {app_name}")

        return success, parse_env_vars(message)

    @staticmethod
    def set_config(session_user: UserSchema, app_name: str, key: str,
                   value: str) -> Tuple[bool, Any]:
        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        return run_command(f"config:set --no-restart {app_name} {key}={value}")

    @staticmethod
    def unset_config(session_user: UserSchema, app_name: str,
                     key: str) -> Tuple[bool, Any]:
        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        return run_command(f"config:unset --no-restart {app_name} {key}")

    @staticmethod
    def apply_config(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        return run_command(f"ps:rebuild {app_name}")
