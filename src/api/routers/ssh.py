from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.schemas import UserSchema
from src.api.services.ssh import SSHService
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
        success, message = await SSHService.register_ssh_key(user.email, public_ssh_key)

        return success, message

    return router
