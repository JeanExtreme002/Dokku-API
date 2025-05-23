from typing import Tuple

from paramiko.client import AutoAddPolicy, SSHClient

from src.config import Config

ssh_hostname = Config.SSH_SERVER.SSH_HOSTNAME
ssh_port = Config.SSH_SERVER.SSH_PORT
ssh_key_path = Config.SSH_SERVER.SSH_KEY_PATH
ssh_key_passphrase = Config.SSH_SERVER.SSH_KEY_PASSPHRASE


def __execute_command(command: str, username: str) -> Tuple[bool, str]:
    """
    Execute a command on the remote server via SSH.

    Args:
        command (str): The command to execute.
        username (str): The SSH username.
    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success
        or failure and the output or error message.
    """
    if username == "root":
        command = f"dokku {command}"

    client = SSHClient()

    try:
        client.set_missing_host_key_policy(AutoAddPolicy())

        client.connect(
            hostname=ssh_hostname,
            port=ssh_port,
            username=username,
            key_filename=ssh_key_path,
            passphrase=ssh_key_passphrase,
        )
        _, stdout, stderr = client.exec_command(command, timeout=60)

        output = stdout.read().decode("utf-8").strip()
        error = stderr.read().decode("utf-8").strip()

        return (True, output) if output else (False, error)

    except Exception as error:
        return False, str(error)

    finally:
        client.close()


def run_command(command: str) -> Tuple[bool, str]:
    """
    Run a command on the remote server via SSH.

    Args:
        command (str): The command to execute.
    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success
        or failure and the output or error message.
    """
    success, message = __execute_command(command, "dokku")
    return success, message


def run_command_as_root(command: str) -> Tuple[bool, str]:
    """
    Run a command on the remote server via SSH as root.

    Args:
        command (str): The command to execute.
    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success
        or failure and the output or error message.
    """
    success, message = __execute_command(command, "root")
    return success, message
