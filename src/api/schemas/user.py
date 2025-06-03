from datetime import datetime
from typing import List

from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    email: str
    access_token: str
    is_admin: bool = False
    created_at: datetime
    apps_quota: int = 0
    services_quota: int = 0
    networks_quota: int = 0
    apps: List[str] = []
    services: List[str] = []
    networks: List[str] = []

    class Config:
        orm_mode = True
