import logging
from abc import ABC
from typing import Any, Tuple

import httpx

from src.config import Config


class SSHService(ABC):

    @staticmethod
    async def register_ssh_key(email: str, public_ssh_key: str) -> Tuple[bool, Any]:
        url = f"{Config.ACL_SERVER.HOST}:{Config.ACL_SERVER.PORT}/api/ssh-keys/register"
        headers = {"MASTER-KEY": Config.MASTER_KEY}
        params = {"user": email.split("@")[0], "public_ssh_key": public_ssh_key}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, params=params)

        message = response.json()
        success = response.status_code == 200

        logging.info(
            f"SSH-KEYS command executed to register a SSH key. Response: {message}"
        )

        return success, message
