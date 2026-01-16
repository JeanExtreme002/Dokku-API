import base64
import os
import tempfile

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.schemas import UserSchema
from src.api.tools.ssh import run_command_as_root
from src.config import Config


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/key/", response_description="Set a SSH key (receive as base64) at Dokku"
    )
    async def set_ssh_key(request: Request, public_ssh_key: str):
        if not Config.API_ALLOW_USERS_REGISTER_SSH_KEY:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "User not allowed to register SSH key"},
            )
        user: UserSchema = request.state.session_user

        with tempfile.NamedTemporaryFile(
            mode="w+b", delete=False, suffix=".pub"
        ) as temp_file:
            content = base64.b64decode(public_ssh_key)
            temp_file.write(bytes(content))
            temp_file_path = temp_file.name

        try:
            command = f"ssh-keys:add {user.email} {temp_file_path}"
            success, message = await run_command_as_root(command)
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": message,
                "success": success,
            },
        )

    return router
