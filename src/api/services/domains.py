import re
from abc import ABC
from typing import Any, Dict, Tuple

from fastapi import HTTPException

from src.api.models import App
from src.api.schemas import UserSchema
from src.api.tools.name import ResourceName
from src.api.tools.ssh import run_command


def parse_domains_report(text: str) -> Dict:
    lines = text.strip().splitlines()
    result = {}

    for line in lines:
        if line.startswith("=====>"):
            continue

        match = re.match(r"^\s*(.+?)\s{2,}(.+)$", line)

        key = (
            match.group(1).strip().strip(":").lower().replace(" ", "_")
            if match
            else line.strip()
        )
        value = match.group(2).strip() if match else ""

        result[key] = value

    if "domains_app_vhosts" in result:
        result["domains_app_vhosts"] = result["domains_app_vhosts"].split()

    return result


class DomainService(ABC):

    @staticmethod
    async def add_domain(
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
        return await run_command(f"domains:add {app_name} {domain}")

    @staticmethod
    async def get_domains_info(
        session_user: UserSchema,
        app_name: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        success, result = await run_command(f"domains:report {app_name}")
        return success, parse_domains_report(result)

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
