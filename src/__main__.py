import asyncio

import uvicorn

from src.api.models import init_models
from src.config import Config


def main() -> None:

    asyncio.run(init_models())

    uvicorn.run(
        "src.api.app:get_app",
        workers=Config.API_WORKERS_COUNT,
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.API_RELOAD,
        log_level=Config.API_LOG_LEVEL,
        factory=True,
    )


if __name__ == "__main__":
    main()
