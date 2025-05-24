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


class PluginsCommands(ABC):

    @staticmethod
    def list_plugins() -> Tuple[bool, Any]:
        success, message = run_command("plugin:list")
        result = parse_plugins(message) if success else message

        return success, result

    @staticmethod
    def is_plugin_installed(plugin_name: str) -> Tuple[bool, Any]:
        success, data = PluginsCommands.list_plugins()

        if not success:
            return False, data

        if plugin_name in data:
            return True, "Plugin is installed"
        return False, "Plugin is not installed"

    @staticmethod
    def install_plugin(plugin_url: str, name: str) -> Tuple[bool, Any]:
        return run_command_as_root(f"plugin:install {plugin_url} --name {name}")

    @staticmethod
    def uninstall_plugin(plugin_name: str) -> Tuple[bool, Any]:
        return run_command_as_root(f"plugin:uninstall {plugin_name}")
