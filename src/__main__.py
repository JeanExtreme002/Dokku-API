import asyncio

import uvicorn

from src.api.models import init_models
from src.config import Config


def main() -> None:

    asyncio.run(init_models())

    uvicorn.run(
        "src.api.app:get_app",
        workers=Config.WORKERS_COUNT,
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.RELOAD,
        log_level=Config.LOG_LEVEL,
        factory=True,
    )


if __name__ == "__main__":
    main()
