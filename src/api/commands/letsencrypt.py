from abc import ABC

from src.api.tools.ssh import run_command


class LetsencryptCommands(ABC):

    @staticmethod
    def set_letsencrypt_mail(email):
        command = f"config:set --global DOKKU_LETSENCRYPT_EMAIL={email}"
        return run_command(command)

    @staticmethod
    def enable_letsencrypt(app_name):
        command = f"letsencrypt:enable {app_name}"
        success, message = run_command(command)

        if "retrieval failed" in message:
            return False, message

        return success, message

    @staticmethod
    def enable_letsencrypt_auto_renewal():
        command = "letsencrypt:cron-job --add"
        return run_command(command)
