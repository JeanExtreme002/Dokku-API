from fastapi import APIRouter, Depends, FastAPI

from src.api.router.api import get_router as api_router
from src.api.router.apps import get_router as apps_router
from src.api.router.base import get_router as base_router
from src.api.router.config import get_router as config_router
from src.api.router.databases import get_router as databases_router
from src.api.router.domains import get_router as domains_router
from src.api.router.letsencrypt import get_router as letsencrypt_router
from src.api.router.plugins import get_router as plugins_router
from src.api.router.users import get_router as users_router
from src.api.tools.validator import (
    validate_api_key,
    validate_master_key,
    validate_user_credentials,
)


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    router.include_router(base_router(router), tags=["Base"])
    router.include_router(api_router(router), tags=["Api"], prefix="/api")
    router.include_router(
        apps_router(router),
        tags=["Apps"],
        prefix="/api/apps",
        dependencies=[Depends(validate_api_key),
                      Depends(validate_user_credentials)],
    )
    router.include_router(
        config_router(router),
        tags=["Config"],
        prefix="/api/config",
        dependencies=[Depends(validate_api_key),
                      Depends(validate_user_credentials)],
    )
    router.include_router(
        databases_router(router),
        tags=["Databases"],
        prefix="/api/databases",
        dependencies=[Depends(validate_api_key),
                      Depends(validate_user_credentials)],
    )
    router.include_router(
        domains_router(router),
        tags=["Domains"],
        prefix="/api/domains",
        dependencies=[Depends(validate_api_key),
                      Depends(validate_user_credentials)],
    )
    router.include_router(
        letsencrypt_router(router),
        tags=["Letsencrypt"],
        prefix="/api/letsencrypt",
        dependencies=[Depends(validate_api_key),
                      Depends(validate_user_credentials)],
    )
    router.include_router(
        plugins_router(router),
        tags=["Plugins"],
        prefix="/api/plugins",
        dependencies=[Depends(validate_api_key),
                      Depends(validate_user_credentials)],
    )
    router.include_router(
        users_router(router),
        tags=["Users"],
        prefix="/api/users",
        dependencies=[Depends(validate_master_key)],
    )

    return router
