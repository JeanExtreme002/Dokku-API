import json
import re
from abc import ABC
from typing import Any, Dict, List, Tuple

from fastapi import HTTPException

from src.api.models import (
    App,
    Network,
    Service,
    create_resource,
    delete_resource,
    get_app_deployment_token,
)
from src.api.schemas import UserSchema
from src.api.services.databases import DatabaseService
from src.api.tools.name import ResourceName
from src.api.tools.ssh import run_command
from src.config import Config


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


class AppService(ABC):

    @staticmethod
    async def create_app(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        _, message = await run_command(f"apps:exists {app_name}")

        if "does not exist" not in message.lower():
            raise HTTPException(status_code=403, detail="App already exists")

        await create_resource(session_user.email, app_name, App)
        return await run_command(f"apps:create {app_name}")

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

        return success, result

    @staticmethod
    async def list_apps(session_user: UserSchema) -> Tuple[bool, Any]:
        result = {}

        for app_name in session_user.apps:
            app_name = str(ResourceName(session_user, app_name, App, from_system=True))
            result[app_name] = (await AppService.get_app_info(session_user, app_name))[
                1
            ]

        return True, result

    @staticmethod
    async def get_logs(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f"logs {app_name}")

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
        session_user: UserSchema, app_name: str
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

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
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

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
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

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
    async def mount_storage(
        session_user: UserSchema,
        app_name: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        app_dir = f"{Config.VOLUME_DIR}/{app_name}"

        return await run_command(f"storage:mount {app_name} {app_dir}:/app")

    @staticmethod
    async def unmount_storage(
        session_user: UserSchema,
        app_name: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        app_dir = f"{Config.VOLUME_DIR}/{app_name}"

        return await run_command(f"storage:unmount {app_name} {app_dir}:/app")
