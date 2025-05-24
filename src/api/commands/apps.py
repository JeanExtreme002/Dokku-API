import json
import re
from abc import ABC
from typing import Any, Dict, Tuple

from fastapi import HTTPException

from src.api.models import App, create_resource, delete_resource
from src.api.models.schema import UserSchema
from src.api.tools.ssh import run_command


def parse_ps_report(message: str) -> Dict:
    lines = message.strip().splitlines()
    result = {}

    for line in lines:
        if line.startswith("=====>"):
            continue

        match = re.match(r"^\s*(.+?)\s{2,}(.+)$", line)

        key = (
            match.group(1).strip().strip(":").lower().replace(" ", "_")
            if match else line.strip()
        )
        value = match.group(2).strip() if match else ""

        result[key] = value

    return result


class AppsCommands(ABC):

    @staticmethod
    def create_app(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        _, message = run_command(f"apps:exists {app_name}")

        if "does not exist" not in message.lower():
            raise HTTPException(status_code=403, detail="App already exists")

        create_resource(session_user.email, app_name, App)
        return run_command(f"apps:create {app_name}")

    @staticmethod
    def delete_app(session_user: UserSchema, app_name: str) -> Tuple[bool, Any]:
        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        delete_resource(session_user.email, app_name, App)
        return run_command(f"--force apps:destroy {app_name}")

    @staticmethod
    def list_apps(session_user: UserSchema) -> Tuple[bool, Any]:
        result = {}

        for app_name in session_user.apps:
            success, message = run_command(f"ps:inspect {app_name}")
            result[app_name] = {}

            if success:
                result[app_name]["data"] = json.loads(message)
                result[app_name]["info_type"] = "inspect"
            else:
                success, message = run_command(f"ps:report {app_name}")
                result[app_name]["data"] = parse_ps_report(message) if success else None
                result[app_name]["info_type"] = "report" if success else None

        return True, result
