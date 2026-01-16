from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.config import Config


class UserSchema(BaseModel):
    id: int
    email: str
    access_token: str
    is_admin: bool = False
    take_over_access_token: Optional[str] = None
    take_over_access_token_expiration: Optional[datetime] = None
    created_at: datetime
    apps_quota: int = Config.API_DEFAULT_APPS_QUOTA
    services_quota: int = Config.API_DEFAULT_SERVICES_QUOTA
    networks_quota: int = Config.API_DEFAULT_NETWORKS_QUOTA
    apps: List[str] = []
    services: List[str] = []
    networks: List[str] = []

    class Config:
        orm_mode = True
