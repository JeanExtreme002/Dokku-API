from abc import ABC

from src.api.tools.ssh import run_command


class DatabasesCommands(ABC):

    @staticmethod
    def create_database(plugin_name, database_name):
        if plugin_name not in ["postgres", "mysql"]:
            return False, "Plugin not found"

        command = f"{plugin_name}:create {database_name}"
        return run_command(command)

    @staticmethod
    def list_databases(plugin_name):
        if plugin_name not in ["postgres", "mysql"]:
            return False, "Plugin not found"

        command = f"{plugin_name}:list"
        return run_command(command)

    @staticmethod
    def database_exists(plugin_name, database_name):
        if plugin_name not in ["postgres", "mysql"]:
            return False, "Plugin not found"

        success, message = DatabasesCommands.list_databases(plugin_name)

        if not success:
            return False, message

        for database in message.split("\n"):
            if database_name in database:
                return True, "Database exists"
        return False, "Database does not exist"

    @staticmethod
    def delete_database(plugin_name, database_name):
        if plugin_name not in ["postgres", "mysql"]:
            return False, "Plugin not found"

        command = f"--force {plugin_name}:destroy {database_name}"
        return run_command(command)

    @staticmethod
    def database_linked_apps(plugin_name, database_name):
        if plugin_name not in ["postgres", "mysql"]:
            return False, "Plugin not found"

        command = f"{plugin_name}:links {database_name}"
        return run_command(command)

    @staticmethod
    def link_database(plugin_name, database_name, app_name):
        if plugin_name not in ["postgres", "mysql"]:
            return False, "Plugin not found"

        command = f"--no-restart {plugin_name}:link {database_name} {app_name}"
        return run_command(command)

    @staticmethod
    def unlink_database(plugin_name, database_name, app_name):
        if plugin_name not in ["postgres", "mysql"]:
            return False, "Plugin not found"

        command = (
            f"--no-restart {plugin_name}:unlink {database_name} {app_name}"
        )
        return run_command(command)
