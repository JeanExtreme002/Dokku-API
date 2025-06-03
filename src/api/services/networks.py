import re
from abc import ABC
from typing import Any, Dict, Tuple

from fastapi import HTTPException

from src.api.models import App, Network, create_resource, delete_resource
from src.api.schemas import UserSchema
from src.api.services import AppService
from src.api.tools.name import ResourceName
from src.api.tools.ssh import run_command


def parse_network_info(message: str) -> Dict:
    lines = message.strip().splitlines()
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

    return result


class NetworkService(ABC):

    @staticmethod
    async def create_network(
        session_user: UserSchema, network_name: str
    ) -> Tuple[bool, Any]:
        network_name = ResourceName(session_user, network_name, Network).for_system()

        _, message = await run_command(f"network:exists {network_name}")

        if "does not exist" not in message.lower():
            raise HTTPException(status_code=403, detail="Network already exists")

        await create_resource(session_user.email, network_name, Network)
        return await run_command(f"network:create {network_name}")

    @staticmethod
    async def delete_network(
        session_user: UserSchema, network_name: str
    ) -> Tuple[bool, Any]:
        network_name = ResourceName(session_user, network_name, Network).for_system()

        if network_name not in session_user.networks:
            raise HTTPException(status_code=404, detail="Network does not exist")

        await delete_resource(session_user.email, network_name, Network)
        return await run_command(f"--force network:destroy {network_name}")

    @staticmethod
    async def list_networks(session_user: UserSchema) -> Tuple[bool, Any]:
        result = {}

        for network_name in session_user.networks:
            parsed_network_name = ResourceName(
                session_user, network_name, Network, from_system=True
            )
            parsed_network_name = str(parsed_network_name)

            success, message = await run_command(f"network:info {network_name}")
            result[parsed_network_name] = None

            if not success:
                result[parsed_network_name] = parse_network_info(message)

        return True, result

    @staticmethod
    async def set_network_to_app(
        session_user: UserSchema,
        network_name: str,
        app_name: str,
    ) -> Tuple[bool, Any]:
        network_name = ResourceName(session_user, network_name, Network).for_system()
        app_name = ResourceName(session_user, app_name, App).for_system()

        if network_name not in session_user.networks:
            raise HTTPException(status_code=404, detail="Network does not exist")

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(
            f"network:set {app_name} attach-post-create {network_name}"
        )

    @staticmethod
    async def unset_network_to_app(
        session_user: UserSchema,
        app_name: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f'network:set {app_name} attach-post-create ""')

    @staticmethod
    async def get_linked_apps(
        session_user: UserSchema,
        network_name: str,
    ) -> Tuple[bool, Any]:
        sys_network_name = ResourceName(
            session_user, network_name, Network
        ).for_system()

        if sys_network_name not in session_user.networks:
            raise HTTPException(status_code=404, detail="Network does not exist")

        results = []

        for app_name in session_user.apps:
            app_name = ResourceName(session_user, app_name, App, from_system=True)
            app_name = str(app_name)

            success, data = await AppService.get_network(session_user, app_name)

            if success and data.get("network", "") == network_name:
                results.append(app_name)

        return True, results
