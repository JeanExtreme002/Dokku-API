from fastapi import APIRouter, Depends, FastAPI, File, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import get_db_session
from src.api.services import GitService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.put("/", response_description="Deploy an application")
    async def deploy_app(
        file: UploadFile = File(...),
        wait: bool = False,
        db_session: AsyncSession = Depends(get_db_session),
    ):
        success, result = await GitService.deploy_application(
            file, db_session, wait=wait
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
