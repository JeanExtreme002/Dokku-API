from typing import List

from pydantic import BaseModel


class UserSchema(BaseModel):
    email: str
    access_token: str
    apps_quote: int
    services_quote: int
    networks_quote: int
    storage_quote: int
    apps: List[str] = []
    services: List[str] = []
    networks: List[str] = []
    storages: List[str] = []

    class Config:
        orm_mode = True
