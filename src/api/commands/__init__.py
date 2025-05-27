from typing import Tuple

from src.api.commands.apps import AppsCommands
from src.api.commands.config import ConfigCommands
from src.api.commands.databases import DatabasesCommands
from src.api.commands.domains import DomainsCommands
from src.api.commands.git import GitCommands
from src.api.commands.letsencrypt import LetsencryptCommands
from src.api.commands.networks import NetworksCommands
from src.api.commands.plugins import PluginsCommands
from src.api.tools.ssh import run_command


async def get_dokku_version() -> Tuple[bool, str]:
    """
    Get the version of Dokku installed on the server.
    """
    return await run_command("version")
