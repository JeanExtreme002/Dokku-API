from fastapi import APIRouter, FastAPI

from src.api.router.api import get_router as api_router
from src.api.router.apps import get_router as app_router
from src.api.router.base import get_router as base_router
from src.api.router.config import get_router as config_router
from src.api.router.databases import get_router as database_router
from src.api.router.domains import get_router as domains_router
from src.api.router.letsencrypt import get_router as letsencrypt_router
from src.api.router.plugins import get_router as plugin_router


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    router.include_router(base_router(router), tags=["Base"])
    router.include_router(api_router(router), tags=["Api"], prefix="/api")
    router.include_router(app_router(router), tags=["Apps"], prefix="/api/apps")
    router.include_router(
        config_router(router), tags=["Config"], prefix="/api/config"
    )
    router.include_router(
        database_router(router), tags=["Databases"], prefix="/api/databases"
    )
    router.include_router(
        domains_router(router), tags=["Domains"], prefix="/api/domains"
    )
    router.include_router(
        letsencrypt_router(router),
        tags=["Letsencrypt"],
        prefix="/api/letsencrypt",
    )
    router.include_router(
        plugin_router(router), tags=["Plugins"], prefix="/api/plugins"
    )

    return router
