from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.models import App, Network, Service
from src.api.schemas import UserSchema
from src.api.services import AppService, DatabaseService
from src.api.tools.name import ResourceName


def get_router(app: FastAPI) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/",
        response_description="Search for apps, services, networks, and more user's resources",
    )
    async def search(request: Request, q: str):
        query = q.strip().lower()
        result = {}

        user: UserSchema = request.state.session_user

        for app_name in user.apps:
            app_name = str(ResourceName(user, app_name, App, from_system=True)).lower()

            if query in app_name:
                details = (await AppService.get_app_info(user, app_name))[1]
                data = result.get("apps", []) + [
                    {app_name: details},
                ]
                result["apps"] = data

        for service_name in user.services:
            plugin_name, service_name = service_name.split(":", maxsplit=1)
            service_name = str(
                ResourceName(user, service_name, Service, from_system=True)
            ).lower()

            if query in service_name:
                details = (
                    await DatabaseService.get_database_info(
                        user, plugin_name, service_name
                    )
                )[1]
                data = result.get("services", []) + [
                    {service_name: details},
                ]
                result["services"] = data

        for network_name in user.networks:
            network_name = str(
                ResourceName(user, network_name, Network, from_system=True)
            ).lower()

            if query in network_name:
                data = result.get("networks", []) + [
                    network_name,
                ]
                result["networks"] = data

        for available_database in (await DatabaseService.list_available_databases())[1]:
            if query in available_database:
                data = result.get("available_databases", []) + [
                    available_database,
                ]
                result["available_databases"] = data

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "result": result,
            },
        )

    return router
