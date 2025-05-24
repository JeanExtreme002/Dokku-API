from typing import Type

from src.api.models.models import App, Resource
from src.api.models.schema import UserSchema


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
        self.__username = user.email.split("@", maxsplit=1)[0]
        self.__separator = {App: "-"}.get(resource_type, "_")
        self.__name = name.lower()

        alphanumeric = "abcdefghijklmnopqrstuvwxyz0123456789"

        if not from_system:
            self.__name = "".join([(char if char in alphanumeric else self.__separator)
                                   for char in self.__name])

        self.__name = (
            self.__name.split(self.__separator, maxsplit=1)[1]
            if from_system else self.__name
        )

    def for_system(self) -> str:
        """
        Get the system resource name for the API system.
        """
        return f"{self.__username}{self.__separator}{self.__name}"

    def normalized(self) -> str:
        """
        Get the normalized resource name for the client.
        """
        return self.__name

    def __str__(self) -> str:
        return self.normalized()
