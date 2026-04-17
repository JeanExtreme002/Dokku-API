import logging
from abc import ABC
from typing import Any, Callable, Coroutine, Tuple

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import get_user, get_users
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
        success = response.status_code == 200

        logging.info(f"ACL command executed: {command}. Response: {message}")

        return success, message

    @staticmethod
    async def sync_apps(
        db_session: AsyncSession,
        on_link_app: Callable[..., Coroutine[Any, Any, Any]],
    ) -> None:
        logging.warning("[sync_acl_apps]::Syncing ACL apps...")

        users = await get_users(db_session)

        for email in users:
            acl_user = email.split("@")[0]
            success, result = await ACLService.run_acl_command(f"allowed {acl_user}")
            result = result["stdout"]

            if not success:
                logging.warning(
                    f"[sync_acl_apps]:{email}::Failed to get allowed apps from ACL"
                )
                continue

            acl_apps = set(line.strip() for line in result.split("\n") if line.strip())

            user = await get_user(email, db_session)
            db_apps = set(user.apps)
            left_apps = db_apps - acl_apps

            for app_name in left_apps:
                logging.warning(
                    f"[sync_acl_apps]:{email}:{app_name}::Importing missing users's app found by ACL to the API..."
                )
                try:
                    await on_link_app(user, app_name, db_session)
                except:
                    logging.warning(
                        f"[sync_acl_apps]:{email}:{app_name}::Failed on importing app to the API..."
                    )

        logging.warning("[sync_acl_apps]::Sync complete.")
