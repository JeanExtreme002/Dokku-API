from abc import ABC

from src.api.tools.ssh import run_command


class AppsCommands(ABC):
    @staticmethod
    def create_app(app_name):
        command = f"apps:create {app_name}"
        return run_command(command)

    @staticmethod
    def delete_app(app_name):
        command = f"--force apps:destroy {app_name}"
        return run_command(command)

    @staticmethod
    def list_apps():
        command = "apps:list"
        return run_command(command)
