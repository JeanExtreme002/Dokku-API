from typing import Tuple

from src.api.services.apps import AppService
from src.api.services.config import ConfigService
from src.api.services.databases import DatabaseService
from src.api.services.domains import DomainService
from src.api.services.git import GitService
from src.api.services.letsencrypt import LetsencryptService
from src.api.services.networks import NetworkService
from src.api.services.plugins import PluginService
from src.api.tools.ssh import run_command


async def get_dokku_version() -> Tuple[bool, str]:
    """
    Get the version of Dokku installed on the server.
    """
    return await run_command("version")
