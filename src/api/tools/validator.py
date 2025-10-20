import re
from typing import Optional

from fastapi import Body, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from src.config import Config


class UserCredentialsPayload(BaseModel):
    access_token: str


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


def validate_admin(
    request: Request,
    master_key_header: Optional[str] = Security(
        APIKeyHeader(
            name="MASTER-KEY",
            auto_error=False,
        )
    ),
    payload: Optional[UserCredentialsPayload] = Body(default=None),
) -> None:
    """
    Check if user is admin or master key is valid.
    """
    if request.state.session_user is not None:
        if request.state.session_user.is_admin:
            return
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="User is not an admin"
        )

    if master_key_header != MASTER_KEY:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid or missing MASTER key"
        )


def validate_api_key(api_key: str) -> None:
    """
    Check if API key is valid.
    """
    if api_key != API_KEY and api_key != MASTER_KEY:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key"
        )


def validate_user_credentials(
    request: Request,
    payload: UserCredentialsPayload = Body(...),
) -> None:
    """
    Check if request.state.session_user is set.
    """
    if request.state.session_user is None and not payload.access_token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing user credentials",
        )


def validate_email_format(email: str) -> None:
    """
    Check if email is in valid format.
    """
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if not re.match(regex, email):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid email format",
        )
    if len(email) > 100:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Email is too long",
        )
