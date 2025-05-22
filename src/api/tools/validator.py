from fastapi import Body, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette.status import HTTP_403_FORBIDDEN

from src.api.config import settings
from src.api.models import get_user

API_KEY = settings.API_KEY
MASTER_KEY = settings.MASTER_KEY


class AuthPayload(BaseModel):
    email: str
    access_token: str


def validate_master_key(
    master_key_header: str = Security(
        APIKeyHeader(name="MASTER-KEY", auto_error=False)
    )
):
    """
    Check if master key is valid.
    """
    if master_key_header == MASTER_KEY:
        return master_key_header

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Invalid or missing MASTER key"
    )


def validate_api_key(api_key: str):
    """
    Check if API key is valid.
    """
    if api_key == API_KEY or api_key == MASTER_KEY:
        return api_key

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Invalid or missing API key"
    )


def validate_user_credentials(payload: AuthPayload = Body(...)):
    """
    Validate user credentials.
    """
    user = get_user(payload.email)

    if user.access_token == payload.access_token:
        return payload

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Invalid or missing access token"
    )
