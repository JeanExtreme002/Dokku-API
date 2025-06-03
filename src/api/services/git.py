import asyncio
import os
import subprocess
import zipfile
from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import Any, Tuple

import aiofiles
from fastapi import HTTPException, UploadFile

from src.api.models import App, get_app_by_deploy_token
from src.api.schemas import UserSchema
from src.api.tools.name import ResourceName
from src.api.tools.ssh import run_command
from src.config import Config


async def save_app_zip(file: UploadFile, dest_dir: Path) -> Tuple[Path, App]:
    temp_zip_path = dest_dir / "repository.zip"
    git_path = dest_dir / ".git"

    deploy_token_filename = ".deployment_token"
    deploy_token_path = dest_dir / deploy_token_filename

    async with aiofiles.open(temp_zip_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    try:
        with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
            zip_ref.extractall(dest_dir)

            if not git_path.exists():
                directories = [p for p in dest_dir.iterdir() if p.is_dir()]

                if len(directories) == 1:
                    dest_dir = dest_dir / directories[0]
                    git_path = dest_dir / ".git"
                    deploy_token_path = dest_dir / deploy_token_filename

            if not git_path.exists():
                error_message = ".git not found in the zip"
                raise HTTPException(detail=error_message, status_code=400)

            if not deploy_token_path.exists():
                error_message = f"File '{deploy_token_filename}' not found in the zip"
                raise HTTPException(detail=error_message, status_code=400)

    except zipfile.BadZipFile:
        raise HTTPException(detail="Bad zip file", status_code=400)

    finally:
        os.remove(temp_zip_path)

    with open(deploy_token_path, "r") as deploy_token_file:
        deploy_token = deploy_token_file.read().strip().strip("\n").strip("\r")

    app, user = await get_app_by_deploy_token(deploy_token)
    return dest_dir, app, user


async def run_git_command(
    *args,
    cwd: Path,
    env: dict = None,
    check: bool = True,
    suppress_errors: bool = False,
):
    process = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(cwd),
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if check and process.returncode != 0:
        if suppress_errors:
            return None
        raise subprocess.CalledProcessError(
            process.returncode, args, output=stdout, stderr=stderr
        )

    return stdout.decode(), stderr.decode()


async def push_to_dokku(
    repo_path: Path,
    dokku_host: str,
    app_name: str,
    branch: str = "main",
):
    env = os.environ.copy()

    env["GIT_SSH_COMMAND"] = (
        f"ssh -i {Config.SSH_SERVER.SSH_KEY_PATH} -o StrictHostKeyChecking=no"
    )

    try:
        await run_git_command(
            "git",
            "remote",
            "remove",
            "dokku",
            cwd=repo_path,
            check=False,
            suppress_errors=True,
        )
        await run_git_command(
            "git",
            "remote",
            "add",
            "dokku",
            f"dokku@{dokku_host}:{app_name}",
            cwd=repo_path,
            check=False,
            suppress_errors=True,
        )

        stdout, _ = await run_git_command(
            "git",
            "push",
            "dokku",
            branch,
            cwd=repo_path,
            env=env,
        )
        return stdout

    except subprocess.CalledProcessError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Git push failed: {error.stderr.decode() or str(error)}",
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while pushing to Dokku: {str(error)}",
        )


class GitService(ABC):

    @staticmethod
    async def deploy_application_by_url(
        session_user: UserSchema,
        app_name: str,
        repo_url: str,
        branch: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        success, message = await run_command(f"git:sync {app_name} {repo_url} {branch}")
        asyncio.create_task(run_command(f"ps:rebuild {app_name}"))

        return success, message

    @staticmethod
    async def deploy_application(
        file: UploadFile,
        wait: bool = False,
    ) -> Tuple[bool, Any]:
        filename = file.filename.split(".")[0]

        SSH_HOSTNAME = Config.SSH_SERVER.SSH_HOSTNAME
        BASE_DIR = Path("/tmp")
        BRANCH = "main"

        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S").split(".")[0]

        dest_dir = BASE_DIR / f"dokku-api-deploy-{filename}-{timestamp}"
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_dir, app, user = await save_app_zip(file, dest_dir)
        app_name = ResourceName(user, app.name, App, from_system=True).for_system()

        task = push_to_dokku(dest_dir, SSH_HOSTNAME, app_name, branch=BRANCH)
        result = "Deploying application..."

        if not wait:
            asyncio.create_task(task)
        else:
            result = await task

        return True, result
