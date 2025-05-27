from fastapi import APIRouter, Depends, FastAPI

from src.api.router.admin import get_router as admin_router
from src.api.router.api import get_router as api_router
from src.api.router.apps import get_router as apps_router
from src.api.router.base import get_router as base_router
from src.api.router.config import get_router as config_router
from src.api.router.databases import get_router as databases_router
from src.api.router.domains import get_router as domains_router
from src.api.router.git import get_router as git_router
from src.api.router.letsencrypt import get_router as letsencrypt_router
from src.api.router.networks import get_router as networks_router
from src.api.router.quota import get_router as quota_router
from src.api.router.search import get_router as search_router
from src.api.router.upload import get_router as upload_router
from src.api.tools.validator import (
    validate_admin,
    validate_api_key,
    validate_user_credentials,
)


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    router.include_router(base_router(router), tags=["Base"])
    router.include_router(api_router(router), tags=["Api"], prefix="/api")
    router.include_router(
        upload_router(app),
        tags=["Deploy"],
        prefix="/api/deploy",
        dependencies=[
            Depends(validate_api_key),
        ],
    )
    router.include_router(
        git_router(app),
        tags=["Deploy"],
        prefix="/api/deploy",
        dependencies=[
            Depends(validate_api_key),
            Depends(validate_user_credentials),
        ],
    )
    router.include_router(
        search_router(app),
        tags=["Search"],
        prefix="/api/search",
        dependencies=[
            Depends(validate_api_key),
            Depends(validate_user_credentials),
        ],
    )
    router.include_router(
        apps_router(app),
        tags=["Apps"],
        prefix="/api/apps",
        dependencies=[
            Depends(validate_api_key),
            Depends(validate_user_credentials),
        ],
    )
    router.include_router(
        config_router(app),
        tags=["Config"],
        prefix="/api/config",
        dependencies=[
            Depends(validate_api_key),
            Depends(validate_user_credentials),
        ],
    )
    router.include_router(
        databases_router(app),
        tags=["Databases"],
        prefix="/api/databases",
        dependencies=[
            Depends(validate_api_key),
            Depends(validate_user_credentials),
        ],
    )
    router.include_router(
        networks_router(app),
        tags=["Networks"],
        prefix="/api/networks",
        dependencies=[
            Depends(validate_api_key),
            Depends(validate_user_credentials),
        ],
    )
    router.include_router(
        domains_router(app),
        tags=["Domains"],
        prefix="/api/domains",
        dependencies=[
            Depends(validate_api_key),
            Depends(validate_user_credentials),
        ],
    )
    router.include_router(
        letsencrypt_router(app),
        tags=["Letsencrypt"],
        prefix="/api/letsencrypt",
        dependencies=[
            Depends(validate_api_key),
            Depends(validate_user_credentials),
        ],
    )
    router.include_router(
        quota_router(app),
        tags=["Quota"],
        prefix="/api/quota",
        dependencies=[
            Depends(validate_api_key),
            Depends(validate_user_credentials),
        ],
    )
    router.include_router(
        admin_router(app),
        tags=["Admin"],
        prefix="/api/admin",
        dependencies=[
            Depends(validate_admin),
        ],
    )

    return router
