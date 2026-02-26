from typing import Optional, Type

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.models import App, AsyncSessionLocal, Resource, get_user
from src.api.schemas import UserSchema
from src.config import Config


class ResourceName:
    """
    Class to define resource names for the API.
    """

    def __init__(
        self,
        user: UserSchema,
        name: str,
        resource_type: Type[Resource],
        from_system: bool = False,
    ):
        self.__user = user.id
        self.__separator = {App: "-"}.get(resource_type, "_")
        self.__name = name.lower()

        allowed = "abcdefghijklmnopqrstuvwxyz0123456789"

        self.__name = "".join(
            [(char if char in allowed else self.__separator) for char in self.__name]
        )

        if from_system and Config.API_USE_PER_USER_RESOURCE_NAMES:
            self.__name = self.__name.lstrip(f"{self.__user}{self.__separator}")

    def for_system(self) -> str:
        """
        Get the system resource name for the API system.
        """
        if Config.API_USE_PER_USER_RESOURCE_NAMES:
            return f"{self.__user}{self.__separator}{self.__name}"
        return self.__name

    def normalized(self) -> str:
        """
        Get the normalized resource name for the client.
        """
        return self.__name

    def __str__(self) -> str:
        return self.normalized()


async def check_shared_app(
    session_user: UserSchema,
    app_name: str,
    shared_by: str,
    db_session: Optional[AsyncSession] = None,
) -> UserSchema:
    """
    Check if the app is being shared by the target user.

    If it's a valid shared app, the function returns the owner.
    """
    if shared_by is None or session_user.email == shared_by:
        return session_user

    if (shared_by, app_name) not in session_user.shared_apps:
        raise HTTPException(
            status_code=404,
            detail="App does not exist or not shared by the owner",
        )

    if db_session is not None:
        return await get_user(shared_by, db_session)

    async with AsyncSessionLocal() as db_session:
        return await get_user(shared_by, db_session)
