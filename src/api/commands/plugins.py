from abc import ABC

from src.api.tools.ssh import run_command, run_command_as_root


class PluginsCommands(ABC):

    @staticmethod
    def list_plugins():
        command = "plugin:list"
        return run_command(command)

    @staticmethod
    def is_plugin_installed(plugin_name):
        success, message = PluginsCommands.list_plugins()

        if not success:
            return False, message

        for plugin in message.split("\n"):
            if plugin_name in plugin:
                return True, "Plugin is installed"
        return False, "Plugin is not installed"

    @staticmethod
    def install_plugin(plugin_name):
        plugins_commands = {
            "postgres": "plugin:install https://github.com/dokku/dokku-postgres.git",
            "mysql": "plugin:install https://github.com/dokku/dokku-mysql.git mysql",
            "letsencrypt":
            "plugin:install https://github.com/dokku/dokku-letsencrypt.git",
        }
        command = plugins_commands.get(plugin_name)

        if not command:
            return False, "Plugin not found"

        return run_command_as_root(command)

    def uninstall_plugin(plugin_name):
        command = f"plugin:uninstall {plugin_name}"
        return run_command_as_root(command)
