import json

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.api.models import get_user_by_access_token


class SessionUserMiddleware(BaseHTTPMiddleware):
    """
    This middleware checks for an access token in the request body and sets the session user accordingly.
    """

    async def dispatch(self, request: Request, call_next):
        request.state.session_user = None

        if not request.headers.get("content-type", "").startswith("application/json"):
            return await call_next(request)

        body_bytes = await request.body()

        try:
            body = json.loads(body_bytes)

            if isinstance(body, dict) and (access_token := body.get("access_token")):
                request.state.session_user = await get_user_by_access_token(
                    access_token
                )

        except HTTPException as error:
            return JSONResponse(
                status_code=error.status_code, content={"detail": error.detail}
            )

        except json.JSONDecodeError:
            pass

        async def receive():
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        request._receive = receive

        return await call_next(request)
