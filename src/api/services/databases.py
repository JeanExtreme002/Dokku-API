import re
from abc import ABC
from typing import Any, Dict, Tuple

from fastapi import HTTPException

from src.api.models import App, Service, create_resource, delete_resource
from src.api.schemas import UserSchema
from src.api.tools.name import ResourceName
from src.api.tools.ssh import run_command
from src.config import Config

available_databases = Config.AVAILABLE_DATABASES


def parse_service_info(plugin_name: str, info_str: str) -> Dict:
    lines = info_str.splitlines()
    result = {}

    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().lower().replace(" ", "_")
            value = value.strip()
            result[key] = value

    result["plugin_name"] = plugin_name
    return result


def extract_database_uri(text):
    pattern = re.compile(
        r"\b(?:[a-z]+)://(?:[^:@\s]+):(?:[^:@\s]+)@(?:[^:@\s]+):\d+/\S+\b",
        re.IGNORECASE,
    )

    match = pattern.search(text)
    return match.group(0) if match else None


class DatabaseService(ABC):

    @staticmethod
    async def list_available_databases() -> Tuple[bool, Any]:
        return True, available_databases

    @staticmethod
    async def create_database(
        session_user: UserSchema,
        plugin_name: str,
        database_name: str,
    ) -> Tuple[bool, Any]:
        database_name = ResourceName(session_user, database_name, Service).for_system()
        available_databases = (await DatabaseService.list_available_databases())[1]

        if plugin_name not in available_databases:
            raise HTTPException(
                status_code=404,
                detail="Plugin not found",
            )

        _, message = await run_command(f"{plugin_name}:exists {database_name}")

        if "does not exist" not in message.lower():
            raise HTTPException(status_code=403, detail="Database already exists")

        await create_resource(
            session_user.email, f"{plugin_name}:{database_name}", Service
        )
        return await run_command(f"{plugin_name}:create {database_name}")

    @staticmethod
    async def list_all_databases(session_user: UserSchema) -> Tuple[bool, Any]:
        available_databases = (await DatabaseService.list_available_databases())[1]
        result = {}

        for plugin_name in available_databases:
            success, data = await DatabaseService.list_databases(
                session_user, plugin_name
            )

            if success and data:
                result[plugin_name] = data

        return True, result

    @staticmethod
    async def list_databases(
        session_user: UserSchema, plugin_name: str
    ) -> Tuple[bool, Any]:
        plugins = [
            plugin
            for plugin in session_user.services
            if plugin.startswith(plugin_name + ":")
        ]
        databases = [plugin.split(":", maxsplit=1)[1] for plugin in plugins]

        result = {}

        for database_name in databases:
            database_name = str(
                ResourceName(session_user, database_name, Service, from_system=True)
            )
            _, data = await DatabaseService.get_database_info(
                session_user, plugin_name, database_name
            )
            result[database_name] = data

        return True, result

    @staticmethod
    async def delete_database(
        session_user: UserSchema,
        plugin_name: str,
        database_name: str,
    ) -> Tuple[bool, Any]:
        database_name = ResourceName(session_user, database_name, Service).for_system()

        if f"{plugin_name}:{database_name}" not in session_user.services:
            raise HTTPException(
                status_code=404,
                detail="Database does not exist",
            )
        await delete_resource(
            session_user.email, f"{plugin_name}:{database_name}", Service
        )
        return await run_command(f"--force {plugin_name}:destroy {database_name}")

    @staticmethod
    async def get_database_info(
        session_user: UserSchema,
        plugin_name: str,
        database_name: str,
    ) -> Tuple[bool, Any]:
        database_name = ResourceName(session_user, database_name, Service).for_system()

        if f"{plugin_name}:{database_name}" not in session_user.services:
            raise HTTPException(
                status_code=404,
                detail="Database does not exist",
            )
        success, message = await run_command(f"{plugin_name}:info {database_name}")
        return success, parse_service_info(plugin_name, message) if success else None

    @staticmethod
    async def get_linked_apps(
        session_user: UserSchema,
        plugin_name: str,
        database_name: str,
    ) -> Tuple[bool, Any]:
        database_name = ResourceName(session_user, database_name, Service).for_system()

        if f"{plugin_name}:{database_name}" not in session_user.services:
            raise HTTPException(
                status_code=404,
                detail="Database does not exist",
            )
        success, message = await run_command(f"{plugin_name}:links {database_name}")
        result = (
            [
                str(ResourceName(session_user, app, App, from_system=True))
                for app in message.split("\n")
                if app
            ]
            if success
            else []
        )

        return success, result

    @staticmethod
    async def link_database(
        session_user: UserSchema,
        plugin_name: str,
        database_name: str,
        app_name: str,
    ) -> Tuple[bool, Any]:
        database_name = ResourceName(session_user, database_name, Service).for_system()
        app_name = ResourceName(session_user, app_name, App).for_system()

        if f"{plugin_name}:{database_name}" not in session_user.services:
            raise HTTPException(
                status_code=404,
                detail="Database does not exist",
            )
        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        return await run_command(
            f"--no-restart {plugin_name}:link {database_name} {app_name}"
        )

    @staticmethod
    async def unlink_database(
        session_user: UserSchema,
        plugin_name: str,
        database_name: str,
        app_name: str,
    ) -> Tuple[bool, Any]:
        database_name = ResourceName(session_user, database_name, Service).for_system()
        app_name = ResourceName(session_user, app_name, App).for_system()

        if f"{plugin_name}:{database_name}" not in session_user.services:
            raise HTTPException(
                status_code=404,
                detail="Database does not exist",
            )
        if app_name not in session_user.apps:
            raise HTTPException(
                status_code=404,
                detail="App does not exist",
            )
        return await run_command(
            f"--no-restart {plugin_name}:unlink {database_name} {app_name}"
        )

    @staticmethod
    async def get_database_uri(
        session_user: UserSchema,
        plugin_name: str,
        database_name: str,
    ) -> Tuple[bool, Any]:
        database_name = ResourceName(session_user, database_name, Service).for_system()

        if f"{plugin_name}:{database_name}" not in session_user.services:
            raise HTTPException(
                status_code=404,
                detail="Database does not exist",
            )

        success, message = await run_command(f"{plugin_name}:info {database_name}")

        if not success:
            return False, None

        return True, extract_database_uri(message)
