import os
import signal
from datetime import datetime

from fastapi import APIRouter, FastAPI, File, UploadFile, status
from fastapi.responses import JSONResponse

from src.api.models import DATABASE_URL
from src.api.tools.ssh import get_command_history, run_command
from src.config import Config


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/run-command/", response_description="Run a dokku command on the server"
    )
    async def run_dokku_command(command: str):
        if not command:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "command is required"},
            )

        if command.startswith("dokku"):
            command = command[len("dokku") :]

        success, message = await run_command(command.strip())

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": message,
                "success": success,
                "command": f"dokku {command}",
            },
        )

    @router.post("/config/", response_description="Return env variables of API server")
    async def get_config():
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "workers_count": Config.WORKERS_COUNT,
                "max_connections_per_request": Config.MAX_CONNECTIONS_PER_REQUEST,
                "reload": Config.RELOAD,
                "log_level": Config.LOG_LEVEL,
                "api_key": Config.API_KEY,
                "api_name": Config.API_NAME,
                "api_version_number": Config.API_VERSION_NUMBER,
                "volume_dir": Config.VOLUME_DIR,
                "ssh_server": {
                    "hostname": Config.SSH_SERVER.SSH_HOSTNAME,
                    "port": Config.SSH_SERVER.SSH_PORT,
                    "key_path": Config.SSH_SERVER.SSH_KEY_PATH,
                },
                "database": {
                    "host": Config.DATABASE.HOST,
                    "port": Config.DATABASE.PORT,
                    "db_name": Config.DATABASE.DB_NAME,
                    "user": Config.DATABASE.DB_USER,
                    "password": Config.DATABASE.DB_PASSWORD,
                    "url": DATABASE_URL,
                },
                "available_databases": Config.AVAILABLE_DATABASES,
            },
        )

    @router.post(
        "/ssh-key/", response_description="Get SSH private key file information"
    )
    async def get_ssh_key_info():
        ssh_key_path = Config.SSH_SERVER.SSH_KEY_PATH

        if not ssh_key_path:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "SSH key path not configured"},
            )

        try:
            if not os.path.exists(ssh_key_path):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"error": "SSH key file not found"},
                )

            stat_info = os.stat(ssh_key_path)

            created_time = datetime.fromtimestamp(stat_info.st_ctime)
            modified_time = datetime.fromtimestamp(stat_info.st_mtime)
            accessed_time = datetime.fromtimestamp(stat_info.st_atime)

            permissions = oct(stat_info.st_mode)[-3:]

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "file_path": ssh_key_path,
                    "directory": os.path.dirname(ssh_key_path),
                    "filename": os.path.basename(ssh_key_path),
                    "size_bytes": stat_info.st_size,
                    "permissions": permissions,
                    "owner_uid": stat_info.st_uid,
                    "group_gid": stat_info.st_gid,
                    "created_at": created_time.isoformat(),
                    "modified_at": modified_time.isoformat(),
                    "accessed_at": accessed_time.isoformat(),
                    "is_readable": os.access(ssh_key_path, os.R_OK),
                    "is_writable": os.access(ssh_key_path, os.W_OK),
                    "is_executable": os.access(ssh_key_path, os.X_OK),
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": f"Failed to get SSH key info: {str(error)}"},
            )

    @router.put("/ssh-key/", response_description="Update SSH private key file")
    async def update_ssh_key(file: UploadFile = File(...)):
        ssh_key_path = Config.SSH_SERVER.SSH_KEY_PATH

        if not ssh_key_path:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "SSH key path not configured"},
            )

        try:
            content = await file.read()

            with open(ssh_key_path, "wb") as ssh_file:
                ssh_file.write(content)

            os.chmod(ssh_key_path, 0o600)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "SSH private key updated successfully",
                    "file_path": ssh_key_path,
                    "file_size": len(content),
                },
            )
        except Exception as error:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": f"Failed to update SSH key: {str(error)}"},
            )

    @router.post("/ssh-history/", response_description="Check SSH command history")
    async def get_ssh_command_history():
        history = get_command_history()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "history": history},
        )

    @router.post("/shutdown/", response_description="Shutdown the API server")
    async def shutdown():
        os.kill(os.getpid(), signal.SIGTERM)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Server is shutting down"},
        )

    return router
