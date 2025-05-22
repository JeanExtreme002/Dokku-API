import os

from pydantic import BaseSettings


class CommonSettings(BaseSettings):
    API_NAME: str = os.getenv("API_NAME")
    API_VERSION_NUMBER: str = os.getenv("API_VERSION_NUMBER")


class ServerSettings(BaseSettings):
    SSH_HOSTNAME: str = os.getenv("SSH_HOSTNAME")
    SSH_PORT: int = os.getenv("SSH_PORT")
    SSH_KEY_PATH: str = os.getenv("SSH_KEY_PATH")
    SSH_KEY_PASSPHRASE: str = os.getenv("SSH_KEY_PASSPHRASE")


class DatabaseSettings(BaseSettings):
    pass


class Settings(CommonSettings, ServerSettings, DatabaseSettings):
    API_KEY: str = os.getenv("API_KEY")
    MASTER_KEY: str = os.getenv("MASTER_KEY")


settings = Settings()
