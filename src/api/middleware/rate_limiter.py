from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware

RATE_LIMIT = ["120 per minute"]


def get_ip_address(request: Request) -> str:
    return request.client.host


def RateLimiterMiddleware(app: FastAPI) -> FastAPI:
    """
    Middleware to apply rate limiting to the FastAPI application.
    """
    limiter = Limiter(key_func=get_ip_address, default_limits=RATE_LIMIT)

    app.state.limiter = limiter
    app.add_exception_handler(429, _rate_limit_exceeded_handler)

    return SlowAPIMiddleware
