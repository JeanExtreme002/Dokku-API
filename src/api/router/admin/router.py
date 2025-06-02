from fastapi import APIRouter, FastAPI

from src.api.router.admin.api import get_router as api_router
from src.api.router.admin.apps import get_router as apps_router
from src.api.router.admin.letsencrypt import get_router as letsencrypt_router
from src.api.router.admin.plugins import get_router as plugins_router
from src.api.router.admin.users import get_router as users_router


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()
    router.include_router(
        api_router(app),
        tags=["Admin: API"],
        prefix="/api",
    )
    router.include_router(
        apps_router(app),
        tags=["Admin: Apps"],
        prefix="/apps",
    )
    router.include_router(
        letsencrypt_router(app),
        tags=["Admin: Letsencrypt"],
        prefix="/letsencrypt",
    )
    router.include_router(
        plugins_router(app),
        tags=["Admin: Plugins"],
        prefix="/plugins",
    )
    router.include_router(
        users_router(app),
        tags=["Admin: Users"],
        prefix="/users",
    )

    return router
