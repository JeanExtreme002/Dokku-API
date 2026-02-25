import os
from typing import List

import dotenv

dotenv.load_dotenv()

API_VERSION_NUMBER = "1.2.13"


class DatabaseConfig:
    """
    Database configuration.
    """

    HOST = os.getenv("DB_HOST", "localhost")
    PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "dokku-api-db")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_URL = os.getenv("DATABASE_URL")


class SSHServerConfig:
    """
    SSH server configuration.
    """

    SSH_HOSTNAME: str = os.getenv("SSH_HOSTNAME")
    SSH_PORT: int = int(os.getenv("SSH_PORT"))
    SSH_KEY_PATH: str = os.getenv("SSH_KEY_PATH")


class Config:
    """
    Base configuration.
    """

    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "5000"))
    API_WORKERS_COUNT = int(os.getenv("API_WORKERS_COUNT", "1"))
    API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"
    API_LOG_LEVEL = os.getenv("API_LOG_LEVEL", "INFO").lower()
    API_MAX_CONNECTIONS_PER_REQUEST = int(
        os.getenv("API_MAX_CONNECTIONS_PER_REQUEST", "1")
    )

    API_NAME: str = os.getenv("API_NAME")
    API_VERSION_NUMBER: str = API_VERSION_NUMBER
    API_ALLOW_USERS_REGISTER_SSH_KEY = (
        os.getenv("API_ALLOW_USERS_REGISTER_SSH_KEY", "true").lower() == "true"
    )
    API_USE_PER_USER_RESOURCE_NAMES = (
        os.getenv("API_USE_PER_USER_RESOURCE_NAMES", "false").lower() == "true"
    )
    API_DEFAULT_APPS_QUOTA = int(os.getenv("API_DEFAULT_APPS_QUOTA", "0"))
    API_DEFAULT_SERVICES_QUOTA = int(os.getenv("API_DEFAULT_SERVICES_QUOTA", "0"))
    API_DEFAULT_NETWORKS_QUOTA = int(os.getenv("API_DEFAULT_NETWORKS_QUOTA", "0"))

    API_KEY: str = os.getenv("API_KEY")
    MASTER_KEY: str = os.getenv("MASTER_KEY")

    VOLUME_DIR: str = os.getenv("VOLUME_DIR")

    SSH_SERVER: SSHServerConfig = SSHServerConfig()
    DATABASE: DatabaseConfig = DatabaseConfig()

    AVAILABLE_DATABASES: List[str] = os.getenv("AVAILABLE_DATABASES", "").split(",")
