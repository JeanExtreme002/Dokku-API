import re
from abc import ABC
from typing import Any, Dict, Tuple

from src.api.tools.ssh import run_command, run_command_as_root


def parse_plugins(text: str) -> Dict:
    lines = text.strip().splitlines()
    plugins = {}

    for line in lines:
        match = re.match(r"^\s*(\S+)\s+(\S+)\s+(enabled|disabled)\s+(.*)$", line)

        if match:
            name = match.group(1)
            version = match.group(2)
            status = match.group(3)
            description = match.group(4).strip()

            plugins[name] = {
                "version": version,
                "status": status,
                "description": description,
            }

    return plugins


class PluginService(ABC):

    @staticmethod
    async def list_plugins() -> Tuple[bool, Any]:
        success, message = await run_command("plugin:list")
        result = parse_plugins(message) if success else message

        return success, result

    @staticmethod
    async def is_plugin_installed(plugin_name: str) -> Tuple[bool, Any]:
        success, data = await PluginService.list_plugins()

        if not success:
            return False, data

        if plugin_name in data:
            return True, "Plugin is installed"
        return False, "Plugin is not installed"

    @staticmethod
    async def install_plugin(plugin_url: str, name: str) -> Tuple[bool, Any]:
        return await run_command_as_root(f"plugin:install {plugin_url} --name {name}")

    @staticmethod
    async def uninstall_plugin(plugin_name: str) -> Tuple[bool, Any]:
        return await run_command_as_root(f"plugin:uninstall {plugin_name}")
