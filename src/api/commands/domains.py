from abc import ABC

from src.api.tools.ssh import run_command


class DomainsCommands(ABC):

    @staticmethod
    def set_domain(app_name, domain):
        command = f"domains:set {app_name} {domain}"
        return run_command(command)

    @staticmethod
    def remove_domain(app_name, domain):
        command = f"domains:remove {app_name} {domain}"
        return run_command(command)
