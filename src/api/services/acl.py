import logging
from abc import ABC
from typing import Any, Tuple

import httpx

from src.config import Config


class ACLService(ABC):

    @staticmethod
    async def run_acl_command(command: str) -> Tuple[bool, Any]:
        url = f"{Config.ACL_SERVER.HOST}:{Config.ACL_SERVER.PORT}/api/run"
        headers = {"MASTER-KEY": Config.MASTER_KEY}
        params = {"command": command}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, params=params)

        message = response.json()
        success = message.get("status", False)
        output = message.get("stdout")

        logging.info(
            f"ACL command executed: {command}. Success: {success}. Output: {output}"
        )

        return success, message
