import logging
import threading
from collections import deque
from datetime import datetime
from typing import Tuple

from paramiko.client import AutoAddPolicy, SSHClient

from src.config import Config

ssh_hostname = Config.SSH_SERVER.SSH_HOSTNAME
ssh_port = Config.SSH_SERVER.SSH_PORT
ssh_key_path = Config.SSH_SERVER.SSH_KEY_PATH

MAX_COMMAND_HISTORY = 1000

command_history = deque(maxlen=MAX_COMMAND_HISTORY)
history_lock = threading.Lock()


def _log_command(command: str) -> None:
    """
    Registra um comando executado no histórico com timestamp.
    """
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} - SSH Command: {command}"

    with history_lock:
        command_history.append(log_entry)


def get_command_history() -> list:
    with history_lock:
        return list(command_history)


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

    _log_command(command)

    client = SSHClient()

    try:
        client.set_missing_host_key_policy(AutoAddPolicy())

        client.connect(
            hostname=ssh_hostname,
            port=ssh_port,
            username=username,
            key_filename=ssh_key_path,
            allow_agent=False,
            look_for_keys=False,
        )
        _, stdout, stderr = client.exec_command(command, timeout=60)

        output = stdout.read().decode("utf-8").strip()
        error = stderr.read().decode("utf-8").strip()

        return (True, output) if output else (False, error)

    except Exception as error:
        return False, str(error)

    finally:
        client.close()


async def run_command(command: str) -> Tuple[bool, str]:
    """
    Run a command on the remote server via SSH.

    Args:
        command (str): The command to execute.
    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success
        or failure and the output or error message.
    """
    success, message = __execute_command(command, "dokku")

    if success:
        logging.info(f"Command executed successfully: {command}")
    else:
        logging.warning(f"Command execution failed: {command}\nError: {message}")
    return success, message


async def run_command_as_root(command: str) -> Tuple[bool, str]:
    """
    Run a command on the remote server via SSH as root.

    Args:
        command (str): The command to execute.
    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success
        or failure and the output or error message.
    """
    success, message = __execute_command(command, "root")

    if success:
        logging.info(f"Command executed successfully: {command}")
    else:
        logging.warning(f"Command execution failed: {command}\nError: {message}")

    return success, message
