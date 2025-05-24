from abc import ABC
from typing import Any, Tuple

from fastapi import HTTPException

from src.api.models import Service, create_resource, delete_resource
from src.api.models.schema import UserSchema
from src.api.tools.ssh import run_command

available_plugins = [
    "postgres",
    "mysql",
    "mongodb",
    "redis",
    "mariadb",
    "couchdb",
    "cassandra",
    "elasticsearch",
    "influxdb",
]


def parse_service_info(info_str):
    result = {}
    lines = info_str.splitlines()

    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().lower().replace(" ", "_")
            value = value.strip()
            result[key] = value

    return result


class DatabasesCommands(ABC):

    @staticmethod
    def create_database(session_user: UserSchema, plugin_name: str,
                        database_name: str) -> Tuple[bool, Any]:
        if plugin_name not in available_plugins:
            raise HTTPException(
                status_code=404,
                detail="Plugin not found",
            )
        create_resource(session_user.email, f"{plugin_name}:{database_name}", Service)
        return run_command(f"{plugin_name}:create {database_name}")

    @staticmethod
    def list_all_databases(session_user: UserSchema) -> Tuple[bool, Any]:
        result = {}

        for plugin_name in available_plugins:
            success, data = DatabasesCommands.list_databases(session_user, plugin_name)
            result[plugin_name] = data if success else None

        return True, result

    @staticmethod
    def list_databases(session_user: UserSchema, plugin_name: str) -> Tuple[bool, Any]:
        plugins = [
            plugin for plugin in session_user.services
            if plugin.startswith(plugin_name + ":")
        ]
        databases = [plugin.split(":", maxsplit=1)[1] for plugin in plugins]

        result = {}

        for database_name in databases:
            success, message = run_command(f"{plugin_name}:info {database_name}")
            result[database_name] = parse_service_info(message) if success else None

        return True, result

    @staticmethod
    def delete_database(session_user: UserSchema, plugin_name: str,
                        database_name: str) -> Tuple[bool, Any]:
        if f"{plugin_name}:{database_name}" not in session_user.services:
            raise HTTPException(
                status_code=404,
                detail="Database does not exist",
            )
        delete_resource(session_user.email, f"{plugin_name}:{database_name}", Service)
        return run_command(f"--force {plugin_name}:destroy {database_name}")

    @staticmethod
    def database_linked_apps(
        session_user: UserSchema, plugin_name: str, database_name: str
    ) -> Tuple[bool, Any]:
        if f"{plugin_name}:{database_name}" not in session_user.services:
            raise HTTPException(
                status_code=404,
                detail="Database does not exist",
            )
        success, message = run_command(f"{plugin_name}:links {database_name}")
        result = [app for app in message.split("\n") if app] if success else None

        return success, result

    @staticmethod
    def link_database(
        session_user: UserSchema, plugin_name: str, database_name: str, app_name: str
    ) -> Tuple[bool, Any]:
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
        return run_command(
            f"--no-restart {plugin_name}:link {database_name} {app_name}"
        )

    @staticmethod
    def unlink_database(
        session_user: UserSchema, plugin_name: str, database_name: str, app_name: str
    ) -> Tuple[bool, Any]:
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
        return run_command(
            f"--no-restart {plugin_name}:unlink {database_name} {app_name}"
        )
