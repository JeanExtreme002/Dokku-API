import os

import dotenv

dotenv.load_dotenv()


class DatabaseConfig:
    """
    Database configuration.
    """

    HOST = os.getenv("DB_HOST", "localhost")
    PORT = int(os.getenv("DB_PORT", "27017"))
    DB_NAME = os.getenv("DB_NAME")


class Config:
    """
    Base configuration.
    """

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    WORKERS_COUNT = int(os.getenv("WORKERS_COUNT", "1"))
    RELOAD = os.getenv("RELOAD", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").lower()
    MAX_CONNECTIONS_PER_REQUEST = int(
        os.getenv("MAX_CONNECTIONS_PER_REQUEST", "1")
    )

    DATABASE: DatabaseConfig = DatabaseConfig()
