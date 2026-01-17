import asyncio
import json
import logging
import re
from abc import ABC
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException

from src.api.models import (
    App,
    Network,
    Service,
    create_resource,
    delete_resource,
    get_app_deployment_token,
    get_resources,
)
from src.api.schemas import UserSchema
from src.api.services.databases import DatabaseService
from src.api.services.domains import DomainService
from src.api.tools.name import ResourceName
from src.api.tools.ssh import run_command
from src.config import Config


def parse_apps_list(text: str):
    """
    Extract the list of apps from a formatted string.
    """
    lines = text.strip().split("\n")
    apps = [
        line.strip() for line in lines if line.strip() and not line.startswith("=====>")
    ]
    return apps


def parse_ps_report(text: str) -> Dict:
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

    return result


def parse_network_info(session_user: UserSchema, text: str) -> Dict:
    result = {}
    lines = text.strip().split("\n")

    for line in lines:
        if "=====>" in line:
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().lower().replace(" ", "_")
            result[key] = value.strip()

    network = result.get("network_attach_post_create")

    if not network:
        network = result.get("network_attach_post_deploy")

    if not network:
        network = result.get("network_computed_attach_post_create")

    if not network:
        network = result.get("network_computed_attach_post_deploy")

    if not network:
        network = result.get("network_computed_initial_network")

    if network:
        network = ResourceName(session_user, network, Network, from_system=True)

    return {"network": str(network) if network else None}


def parse_port_mappings(text: str) -> List:
    lines = text.strip().splitlines()

    ports = []

    for line in lines:
        parts = line.strip().split()

        if len(parts) == 3:
            scheme, host_port, container_port = parts
            ports.append(
                {
                    "protocol": scheme,
                    "origin": int(host_port),
                    "dest": int(container_port),
                }
            )

    return ports


def get_user_id_from_app(name) -> Optional[int]:
    id = name.split("-", maxsplit=1)[0]

    try:
        return int(id)
    except ValueError:
        return None


def get_raw_app(name):
    return name.split("-", maxsplit=1)[-1]


def parse_xxd_to_bytes(text: str) -> bytes:
    """
    Convert standard `xxd` output into raw bytes.

    Handles default xxd format lines like:
    "00000000: 25504446 2d312e33 0a25e2e3 cf...  ........"
    by extracting hex columns before the double-space ASCII separator.
    Falls back to extracting all 2-hex-digit tokens if needed.
    """
    lines = text.strip().splitlines()
    hex_chunks = []

    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        if ":" not in line:
            # skip non-data lines
            continue
        try:
            after = line.split(":", 1)[1]
            # hex column is before two spaces that precede ASCII area
            hex_part = after.split("  ", 1)[0]
            hex_str = hex_part.replace(" ", "")
            if hex_str:
                hex_chunks.append(hex_str)
        except Exception:
            continue

    if hex_chunks:
        hex_data = "".join(hex_chunks)
        try:
            return bytes.fromhex(hex_data)
        except ValueError:
            pass

    # Fallback: collect all byte-sized hex tokens
    tokens = re.findall(r"\b[0-9a-fA-F]{2}\b", text)
    return bytes(int(t, 16) for t in tokens)


class AppService(ABC):

    @staticmethod
    async def create_app(
        session_user: UserSchema, app_name: str, unique_app: Optional[bool] = False
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if unique_app:
            success, message = await run_command("apps:list")

            if not success:
                raise HTTPException(
                    status_code=500, detail="Could not recover apps list"
                )

            apps = parse_apps_list(message)

            app_exists = any(
                [get_raw_app(app) == get_raw_app(app_name) for app in apps]
            )

            if app_exists:
                raise HTTPException(status_code=403, detail="App name already in use")
        else:
            _, message = await run_command(f"apps:exists {app_name}")

            if "does not exist" not in message.lower():
                raise HTTPException(status_code=403, detail="App already exists")

        await create_resource(session_user.email, app_name, App)
        success, message = await run_command(f"apps:create {app_name}")

        if unique_app and success:
            session_user.apps.append(app_name)
            app_name = get_raw_app(app_name)
            await DomainService.set_domain(
                session_user, app_name, f"{app_name}.{Config.SSH_SERVER.SSH_HOSTNAME}"
            )

        return success, message

    @staticmethod
    async def get_deployment_token(
        session_user: UserSchema,
        app_name: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        deploy_token = await get_app_deployment_token(app_name)

        return True, deploy_token

    @staticmethod
    async def delete_app(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        await delete_resource(session_user.email, app_name, App)
        return await run_command(f"--force apps:destroy {app_name}")

    @staticmethod
    async def execute_command(
        session_user: UserSchema, app_name: str, container_type: str, command: str
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f"enter {app_name} {container_type} {command}")

    @staticmethod
    async def get_app_url(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f"url {app_name}")

    @staticmethod
    async def get_app_info(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        success, message = await run_command(f"ps:inspect {app_name}")
        result = {}

        if success:
            result["data"] = json.loads(message)
            result["info_origin"] = "inspect"
        else:
            success, message = await run_command(f"ps:report {app_name}")
            result["data"] = parse_ps_report(message) if success else None
            result["info_origin"] = "report" if success else None

        result["raw_name"] = app_name
        return success, result

    @staticmethod
    async def list_apps(
        session_user: UserSchema, return_info: bool = True
    ) -> Tuple[bool, Any]:
        result = {}

        tasks = []
        app_names = []

        if not return_info:
            for app_name in session_user.apps:
                app_name = str(
                    ResourceName(session_user, app_name, App, from_system=True)
                )
                result[app_name] = {}
            return True, result

        for app_name in session_user.apps:
            app_name = str(ResourceName(session_user, app_name, App, from_system=True))
            app_names.append(app_name)
            tasks.append(AppService.get_app_info(session_user, app_name))

        app_infos = await asyncio.gather(*tasks, return_exceptions=True)

        for name, info in zip(app_names, app_infos):
            result[name] = {} if isinstance(info, Exception) else info[1]

        return True, result

    @staticmethod
    async def get_logs(
        session_user: UserSchema, app_name: str, n_lines: int = 2000
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f"logs {app_name} --num {n_lines}")

    @staticmethod
    async def start_app(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f"ps:start {app_name}")

    @staticmethod
    async def stop_app(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f"ps:stop {app_name}")

    @staticmethod
    async def restart_app(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f"ps:restart {app_name}")

    @staticmethod
    async def rebuild_app(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f"ps:rebuild {app_name}")

    @staticmethod
    async def get_builder(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        success, message = await run_command(f"builder:report {app_name}")

        if not success:
            return False, message

        result = {}
        lines = message.strip().split("\n")

        for line in lines:
            if ":" in line:
                key, value = line.split(":", maxsplit=1)
                key = key.strip().lower().replace(" ", "_")
                result[key] = value.strip()

        return True, result

    @staticmethod
    async def set_builder(
        session_user: UserSchema, app_name: str, builder: str
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        available_builders = ["herokuish", "dockerfile", "lambda", "pack"]

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        if builder not in available_builders:
            message = (
                f"Invalid builder. Available builders: {', '.join(available_builders)}"
            )
            raise HTTPException(
                status_code=400,
                detail=message,
            )

        return await run_command(f"builder:set {app_name} selected {builder}")

    @staticmethod
    async def get_network(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        success, message = await run_command(f"network:report {app_name}")

        if not success:
            return False, message

        return True, parse_network_info(session_user, message)

    @staticmethod
    async def list_port_mappings(
        session_user: UserSchema, app_name: str, use_proxy: bool = False
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        if use_proxy:
            success, message = await run_command(f"proxy:ports {app_name}")
        else:
            success, message = await run_command(f"ports:list {app_name}")

        if "no port mappings" in message.lower():
            return True, []

        if not success:
            return False, message

        return True, parse_port_mappings(message)

    @staticmethod
    async def add_port_mapping(
        session_user: UserSchema,
        app_name: str,
        origin_port: int,
        dest_port: int,
        protocol: str,
        use_proxy: bool = False,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        if use_proxy:
            return await run_command(
                f"proxy:ports-add {app_name} {protocol}:{origin_port}:{dest_port}"
            )
        else:
            return await run_command(
                f"ports:add {app_name} {protocol}:{origin_port}:{dest_port}"
            )

    @staticmethod
    async def remove_port_mapping(
        session_user: UserSchema,
        app_name: str,
        origin_port: int,
        dest_port: int,
        protocol: str,
        use_proxy: bool = False,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        if use_proxy:
            return await run_command(
                f"proxy:ports-remove {app_name} {protocol}:{origin_port}:{dest_port}"
            )
        else:
            return await run_command(
                f"ports:remove {app_name} {protocol}:{origin_port}:{dest_port}"
            )

    @staticmethod
    async def get_linked_databases(
        session_user: UserSchema,
        app_name: str,
    ) -> Tuple[bool, Any]:
        sys_app_name = ResourceName(session_user, app_name, App).for_system()

        if sys_app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        result = {}

        for db_name in session_user.services:
            plugin_name, db_name = db_name.split(":", maxsplit=1)
            db_name = str(
                ResourceName(session_user, db_name, Service, from_system=True)
            )

            success, data = await DatabaseService.get_linked_apps(
                session_user, plugin_name, db_name
            )

            if success and app_name in data:
                result[plugin_name] = result.get(plugin_name, []) + [
                    db_name,
                ]

        return True, result

    @staticmethod
    async def list_storage(
        session_user: UserSchema,
        app_name: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        success, result = await run_command(f"storage:list {app_name}")
        return success, (result.split("\n") if result else [])

    @staticmethod
    async def mount_storage(
        session_user: UserSchema,
        app_name: str,
        directory: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        app_dir = f"{Config.VOLUME_DIR}/{app_name}"

        return await run_command(f"storage:mount {app_name} {app_dir}:{directory}")

    @staticmethod
    async def unmount_storage(
        session_user: UserSchema,
        app_name: str,
        directory: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        app_dir = f"{Config.VOLUME_DIR}/{app_name}"

        return await run_command(f"storage:unmount {app_name} {app_dir}:{directory}")

    @staticmethod
    async def download_file(
        session_user: UserSchema,
        app_name: str,
        filename: str,
    ) -> Tuple[bool, Any]:
        """
        Run `xxd {filename}` inside the app's web container and reconstruct bytes.

        Returns (success, bytes) on success, else (False, error_message).
        """
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        success, output = await run_command(f"enter {app_name} web xxd {filename}")

        if not success:
            return False, output

        try:
            data = parse_xxd_to_bytes(output)
            return True, data
        except Exception as error:
            return False, f"Failed to parse xxd output: {error}"

    @staticmethod
    async def sync_dokku_with_api_database() -> None:
        success, message = await run_command("apps:list")

        if not success:
            logging.warning("Could not recover apps list to sync with database")
            return

        logging.warning("[sync_dokku_w_app_database]::Syncing Dokku...")

        apps = parse_apps_list(message)
        apps = {name: True for name in apps if get_user_id_from_app(name) is not None}

        db_apps = await get_resources(App, offset=0, limit=None)

        for app in db_apps:
            apps.pop(app["name"], None)

        for app_name in apps:
            logging.warning(
                f"[sync_dokku_w_app_database]:{app_name}::Destroying unused application..."
            )
            await run_command(f"--force apps:destroy {app_name}")

        logging.warning("[sync_dokku_w_app_database]::Sync complete.")
