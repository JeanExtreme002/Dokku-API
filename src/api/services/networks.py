import asyncio
import logging
import re
from abc import ABC
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import App, Network, create_resource, delete_resource, get_resources
from src.api.schemas import UserSchema
from src.api.services import AppService
from src.api.tools.resource import ResourceName
from src.api.tools.ssh import run_command
from src.config import Config


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


def parse_networks_list(text: str):
    """
    Extract the list of networks from a formatted string.
    """
    lines = text.strip().split("\n")
    networks = [
        line.strip() for line in lines if line.strip() and not line.startswith("=====>")
    ]
    return networks


def get_user_id_from_network(name) -> Optional[int]:
    id = name.split("-", maxsplit=1)[0]

    try:
        return int(id)
    except ValueError:
        return None


class NetworkService(ABC):

    @staticmethod
    async def create_network(
        session_user: UserSchema, network_name: str, db_session: AsyncSession
    ) -> Tuple[bool, Any]:
        network_name = ResourceName(session_user, network_name, Network).for_system()

        _, message = await run_command(f"network:exists {network_name}")

        if "does not exist" not in message.lower():
            raise HTTPException(status_code=403, detail="Network already exists")

        await create_resource(session_user.email, network_name, Network, db_session)
        return await run_command(f"network:create {network_name}")

    @staticmethod
    async def delete_network(
        session_user: UserSchema, network_name: str, db_session: AsyncSession
    ) -> Tuple[bool, Any]:
        network_name = ResourceName(session_user, network_name, Network).for_system()

        if network_name not in session_user.networks:
            raise HTTPException(status_code=404, detail="Network does not exist")

        await delete_resource(session_user.email, network_name, Network, db_session)
        return await run_command(f"--force network:destroy {network_name}")

    @staticmethod
    async def list_networks(
        session_user: UserSchema, return_info: bool = True
    ) -> Tuple[bool, Any]:
        result = {}

        tasks = []
        network_names = []
        parsed_network_names = []

        if not return_info:
            for network_name in session_user.networks:
                parsed_network_name = ResourceName(
                    session_user, network_name, Network, from_system=True
                )
                parsed_network_name = str(parsed_network_name)
                result[parsed_network_name] = {}
            return True, result

        for network_name in session_user.networks:
            parsed_network_name = ResourceName(
                session_user, network_name, Network, from_system=True
            )
            parsed_network_name = str(parsed_network_name)

            network_names.append(network_name)
            parsed_network_names.append(parsed_network_name)
            tasks.append(run_command(f"network:info {network_name}"))

        network_infos = await asyncio.gather(*tasks, return_exceptions=True)

        for name, info in zip(parsed_network_names, network_infos):
            result[name] = None

            if not isinstance(info, Exception):
                success, message = info
                if success:
                    result[name] = parse_network_info(message)

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

    @staticmethod
    async def sync_dokku_with_api_database(db_session: AsyncSession) -> None:
        if not Config.API_USE_PER_USER_RESOURCE_NAMES:
            logging.warning(
                "[sync_dokku_w_network_database]::Not implemented on API_USE_PER_USER_RESOURCE_NAMES=false..."
            )
            return

        success, message = await run_command("network:list", use_log=False)

        if not success:
            logging.warning("Could not recover networks list to sync with database")
            return

        logging.warning("[sync_dokku_w_network_database]::Syncing Dokku...")

        networks = parse_networks_list(message)
        networks = {
            name: True
            for name in networks
            if get_user_id_from_network(name) is not None
        }

        db_networks = await get_resources(
            Network, offset=0, limit=None, db_session=db_session
        )

        for network in db_networks:
            networks.pop(network["name"], None)

        for network_name in networks:
            logging.warning(
                f"[sync_dokku_w_network_database]:{network_name}::Destroying unused network..."
            )
            await run_command(f"--force network:destroy {network_name}", use_log=False)

        logging.warning("[sync_dokku_w_network_database]::Sync complete.")
