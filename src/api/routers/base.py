from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_description="Index")
    async def index(request: Request):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "OK",
                "message": "Visit /docs to learn more about the API!",
            },
        )

    return router
