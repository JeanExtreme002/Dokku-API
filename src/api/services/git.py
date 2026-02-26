import asyncio
import logging
import os
import subprocess
import zipfile
from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import Any, Tuple

import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import App, get_app_by_deploy_token
from src.api.schemas import UserSchema
from src.api.tools.resource import ResourceName
from src.api.tools.ssh import run_command
from src.config import Config


async def save_app_zip(
    file: UploadFile, dest_dir: Path, db_session: AsyncSession
) -> Tuple[Path, App]:
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

    app, user = await get_app_by_deploy_token(deploy_token, db_session)
    return dest_dir, app, user


async def run_git_command(
    *args,
    cwd: Path,
    env: dict = None,
    check: bool = True,
    suppress_errors: bool = False,
    timeout: int = 30,
):
    process = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(cwd),
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        process.kill()
        if not suppress_errors:
            raise subprocess.CalledProcessError(
                -1, args, output=b"", stderr=b"Command timed out"
            )
        return None

    stdout_str = stdout.decode() if stdout else ""
    stderr_str = stderr.decode() if stderr else ""

    if check and process.returncode != 0:
        if suppress_errors:
            return None
        raise subprocess.CalledProcessError(
            process.returncode, args, output=stdout, stderr=stderr
        )

    return stdout_str, stderr_str


async def push_to_dokku(
    repo_path: Path,
    dokku_host: str,
    dokku_port: int,
    app_name: str,
    branch: str = "master",
):
    logging.info(
        f"[push_to_dokku]:{app_name}:{branch}::Preparing to push application..."
    )
    env = os.environ.copy()

    env["GIT_SSH_COMMAND"] = (
        f"ssh -i {Config.SSH_SERVER.SSH_KEY_PATH} -p {dokku_port} "
        f"-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
        f"-o IdentitiesOnly=yes -o LogLevel=VERBOSE"
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
        logging.info(f"[push_to_dokku]:{app_name}:{branch}::Set up the remote in Git.")

        try:
            await run_git_command(
                "git",
                "show-ref",
                "--verify",
                f"refs/heads/{branch}",
                cwd=repo_path,
                check=True,
            )
            logging.info(
                f"[push_to_dokku]:{app_name}:{branch}::Branch successfully detected."
            )
        except subprocess.CalledProcessError:
            current_branch_stdout, _ = await run_git_command(
                "git",
                "rev-parse",
                "--abbrev-ref",
                "HEAD",
                cwd=repo_path,
                check=True,
            )
            branch = current_branch_stdout.strip()
            logging.info(
                f"[push_to_dokku]:{app_name}:{branch}::Set up the current branch by 'git rev-parse'."
            )

        process = await asyncio.create_subprocess_exec(
            "git",
            "push",
            "-v",
            "dokku",
            f"{branch}:master",
            "--force",
            cwd=str(repo_path),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=30 * 60
            )
            output = stdout.decode() if stdout else ""
            error = stderr.decode() if stderr else ""

            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode,
                    ["git", "push", "dokku", f"{branch}:master", "--force"],
                    output=stdout,
                )
            if error:
                logging.info(
                    f"[push_to_dokku]:{app_name}:{branch}::Something went wrong... {error}"
                )

            logging.info(
                f"[push_to_dokku]:{app_name}:{branch}::Finished deployment. {output}"
            )
            return f"{output}{error}"

        except asyncio.TimeoutError:
            logging.info(f"[push_to_dokku]:{app_name}:{branch}::Timeout error.")
            process.kill()
            raise HTTPException(
                status_code=500, detail="Git push timed out after 30 minutes"
            )

    except subprocess.CalledProcessError as error:
        error_output = error.output.decode() if error.output else str(error)

        if (
            "Warning: Permanently added" in error_output
            and len(error_output.strip().split("\n")) == 1
        ):
            detail = (
                "SSH connection succeeded but push appears to be hanging. "
                "This might indicate a network issue or the Dokku server is not responding properly. "
                f"Full output: {error_output}"
            )
        elif "Everything up-to-date" in error_output:
            logging.info(f"[push_to_dokku]:{app_name}:{branch}::Everything up-to-date.")
            return "No changes to push - everything is up-to-date"
        elif "non-fast-forward" in error_output:
            detail = (
                "Push rejected due to non-fast-forward. "
                "The remote repository has changes that conflict with your push. "
                f"Output: {error_output}"
            )
        else:
            detail = (
                f"Git push failed with return code {error.returncode}: {error_output}"
            )

        logging.info(f"[push_to_dokku]:{app_name}:{branch}::Error:{detail}.")
        raise HTTPException(status_code=500, detail=detail)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while pushing to Dokku: {str(error)}",
        )


def parse_git_info(text: str) -> dict:
    lines = text.strip().splitlines()
    result = {}

    for line in lines:
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()

    return result


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
    async def get_deployment_info(
        session_user: UserSchema,
        app_name: str,
    ) -> Tuple[bool, Any]:
        app_name = ResourceName(session_user, app_name, App).for_system()

        if app_name not in session_user.apps:
            raise HTTPException(status_code=404, detail="App does not exist")

        success, message = await run_command(f"git:report {app_name}")
        return success, parse_git_info(message)

    @staticmethod
    async def deploy_application(
        file: UploadFile,
        db_session: AsyncSession,
        wait: bool = False,
    ) -> Tuple[bool, Any]:
        filename = file.filename.split(".")[0]

        SSH_HOSTNAME = Config.SSH_SERVER.SSH_HOSTNAME
        SSH_PORT = Config.SSH_SERVER.SSH_PORT
        BASE_DIR = Path("/tmp")
        BRANCH = "master"

        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S").split(".")[0]

        dest_dir = BASE_DIR / f"dokku-api-deploy-{filename}-{timestamp}"
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_dir, app, user = await save_app_zip(file, dest_dir, db_session)
        app_name = ResourceName(user, app.name, App, from_system=True).for_system()

        task = push_to_dokku(dest_dir, SSH_HOSTNAME, SSH_PORT, app_name, branch=BRANCH)
        result = "Deploying application..."

        if not wait:
            asyncio.create_task(task)
        else:
            result = await task

        return True, result
