import logging
from typing import Tuple

import asyncssh

from src.config import Config

ssh_hostname = Config.SSH_SERVER.SSH_HOSTNAME
ssh_port = Config.SSH_SERVER.SSH_PORT
ssh_key_path = Config.SSH_SERVER.SSH_KEY_PATH


async def _log_command(command: str, username: str) -> None:
    """
    Save an executed command to the history (database).

    The write uses its own session and any failure is only logged, so that
    recording the history never interrupts the command execution.
    """
    # Lazy import to avoid a circular import: the src.api.tools package is
    # imported by src.api.models.tools.
    from src.api.models import AsyncSessionLocal, log_command

    try:
        async with AsyncSessionLocal() as db_session:
            await log_command(command, username, db_session)
    except Exception as error:
        logging.warning(f"Failed to save command to history: {error}")


async def __execute_command(
    command: str, username: str, use_log: bool = True, dry_run: bool = False
) -> Tuple[bool, str]:
    """
    Execute a command on the remote server via SSH.

    Args:
        command (str): The command to execute.
        username (str): The SSH username.
        use_log (bool): If True, save the command to the command history (database).
        dry_run (bool): If True, the command is not actually executed.
    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success
        or failure and the output or error message.
    """
    if username == "root":
        command = f"dokku {command}"

    if use_log:
        await _log_command(command, username)

    if dry_run:
        return True, ""

    try:
        async with asyncssh.connect(
            host=ssh_hostname,
            port=ssh_port,
            username=username,
            client_keys=[ssh_key_path],
            known_hosts=None,
            connect_timeout=30,
        ) as conn:
            result = await conn.run(command, timeout=10 * 60)

            if result.exit_status == 0:
                output = result.stdout.strip() if result.stdout else ""
                return (True, output)
            else:
                output = result.stdout.strip() if result.stdout else ""
                error = (
                    result.stderr.strip()
                    if result.stderr
                    else f"Command failed with exit code {result.exit_status}"
                )

                output = f"{output}\n{error}" if output else error

                return (False, output)

    except Exception as error:
        return False, str(error)


async def run_command(
    command: str, use_log: bool = True, dry_run: bool = False
) -> Tuple[bool, str]:
    """
    Run a command on the remote server via SSH.

    Args:
        command (str): The command to execute.
        use_log (bool): If True, save the command to the command history (database).
        dry_run (bool): If True, the command is not actually executed.
    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success
        or failure and the output or error message.
    """
    success, message = await __execute_command(
        command, "dokku", use_log=use_log, dry_run=dry_run
    )

    if success:
        logging.info(f"Command executed successfully: {command}")
    else:
        logging.warning(f"Command execution failed: {command}\nError: {message}")
    return success, message


async def run_command_as_root(
    command: str, use_log: bool = True, dry_run: bool = False
) -> Tuple[bool, str]:
    """
    Run a command on the remote server via SSH as root.

    Args:
        command (str): The command to execute.
        use_log (bool): If True, save the command to the command history (database).
        dry_run (bool): If True, the command is not actually executed.
    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success
        or failure and the output or error message.
    """
    success, message = await __execute_command(
        command, "root", use_log=use_log, dry_run=dry_run
    )

    if success:
        logging.info(f"Command executed successfully: {command}")
    else:
        logging.warning(f"Command execution failed: {command}\nError: {message}")

    return success, message
