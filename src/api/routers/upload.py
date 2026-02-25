from fastapi import APIRouter, FastAPI, File, UploadFile, status
from fastapi.responses import JSONResponse

from src.api.services import GitService


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.put("/", response_description="Deploy an application")
    async def deploy_app(file: UploadFile = File(...), wait: bool = False):
        success, result = await GitService.deploy_application(file, wait=wait)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": success,
                "result": result,
            },
        )

    return router
