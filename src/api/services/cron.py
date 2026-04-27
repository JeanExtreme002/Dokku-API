import re
from abc import ABC
from typing import Any, List, Optional, Tuple

from fastapi import HTTPException

from src.api.models import App
from src.api.schemas import UserSchema
from src.api.tools.resource import ResourceName, check_shared_app
from src.api.tools.ssh import run_command


def parse_cron_list(text: str) -> List[dict]:
    lines = text.strip().splitlines()

    header_index = next(
        (
            i
            for i, line in enumerate(lines)
            if line.strip() and not line.startswith("=====>")
        ),
        None,
    )
    if header_index is None or header_index + 1 >= len(lines):
        return []

    header = lines[header_index]

    # Detect column names and their char positions dynamically.
    # Columns in Dokku tabular output are separated by 2+ spaces.
    col_matches = list(re.finditer(r"(?:^|\s{2,})(\S+)", header))
    columns = [(m.group(1), m.start(1)) for m in col_matches]

    result = []
    for line in lines[header_index + 1 :]:
        if not line.strip():
            continue
        row = {}
        for i, (col_name, start) in enumerate(columns):
            end = columns[i + 1][1] if i + 1 < len(columns) else None
            value = line[start:end].strip() if end else line[start:].strip()
            row[col_name.lower()] = value
        result.append(row)

    return result


class CronService(ABC):

    @staticmethod
    async def list_cron(
        session_user: UserSchema,
        app_name: str,
        shared_by: Optional[str] = None,
    ) -> Tuple[bool, Any]:
        session_user = await check_shared_app(session_user, app_name, shared_by)
        app_name = ResourceName(session_user, app_name).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        success, message = await run_command(f"cron:list {app_name}")

        if not success:
            return False, message

        return True, parse_cron_list(message)

    @staticmethod
    async def run_cron(
        session_user: UserSchema,
        app_name: str,
        cron_id: str,
        shared_by: Optional[str] = None,
    ) -> Tuple[bool, Any]:
        session_user = await check_shared_app(session_user, app_name, shared_by)
        app_name = ResourceName(session_user, app_name).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        return await run_command(f"cron:run {app_name} {cron_id}")
