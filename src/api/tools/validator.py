from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from src.api.config import settings

API_KEY = settings.API_KEY


def validate_api_key(
    api_key_header: str = Security(
        APIKeyHeader(name="API-KEY", auto_error=False)
    )
):
    """
    Check if API key is valid.
    """
    if api_key_header == API_KEY:
        return api_key_header

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Invalid or missing API key"
    )
