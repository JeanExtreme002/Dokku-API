from fastapi import Body, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette.status import HTTP_403_FORBIDDEN

from src.api.models import get_user
from src.config import Config

API_KEY = Config.API_KEY
MASTER_KEY = Config.MASTER_KEY

if MASTER_KEY is None:
    raise ValueError("MASTER_KEY must be set in the environment variables")

if " " in MASTER_KEY:
    raise ValueError("MASTER_KEY must not contain spaces")

if len(MASTER_KEY) < 8:
    raise ValueError("MASTER_KEY must be at least 8 characters long")

if " " in API_KEY:
    raise ValueError("API_KEY must not contain spaces")


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
