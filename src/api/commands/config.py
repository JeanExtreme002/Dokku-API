from abc import ABC

from src.api.tools.ssh import run_command


class ConfigCommands(ABC):

    @staticmethod
    def list_config(app_name):
        command = f"config:show {app_name}"
        return run_command(command)

    @staticmethod
    def set_config(app_name, key, value):
        command = f"config:set --no-restart {app_name} {key}={value}"
        return run_command(command)

    @staticmethod
    def unset_config(app_name, key):
        command = f"config:unset --no-restart {app_name} {key}"
        return run_command(command)

    @staticmethod
    def apply_config(app_name):
        command = f"ps:rebuild {app_name}"
        return run_command(command)
