from typing import List

from pydantic import BaseModel


class UserSchema(BaseModel):
    email: str
    access_token: str
    is_admin: bool = False
    apps_quota: int = 0
    services_quota: int = 0
    networks_quota: int = 0
    storage_quota: int = 0
    apps: List[str] = []
    services: List[str] = []
    networks: List[str] = []
    storages: List[str] = []

    class Config:
        orm_mode = True
