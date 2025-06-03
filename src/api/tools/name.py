from typing import Type

from src.api.models.models import App, Resource
from src.api.schemas import UserSchema


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

        if from_system:
            self.__name = self.__name.lstrip(f"{self.__user}{self.__separator}")

    def for_system(self) -> str:
        """
        Get the system resource name for the API system.
        """
        return f"{self.__user}{self.__separator}{self.__name}"

    def normalized(self) -> str:
        """
        Get the normalized resource name for the client.
        """
        return self.__name

    def __str__(self) -> str:
        return self.normalized()
