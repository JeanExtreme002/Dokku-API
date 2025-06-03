import datetime
import secrets
import time
from typing import List, Tuple, Type

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from src.api.models.base import (
    USER_EAGER_LOAD,
    App,
    Base,
    Network,
    Resource,
    Service,
    User,
)
from src.api.schemas import UserSchema
from src.api.tools import hash_access_token, validate_email_format
from src.config import Config

DB_USER = Config.DATABASE.DB_USER
DB_PASSWORD = Config.DATABASE.DB_PASSWORD
DB_HOST = Config.DATABASE.HOST
DB_PORT = Config.DATABASE.PORT
DB_NAME = Config.DATABASE.DB_NAME

DATABASE_URL = Config.DATABASE.DB_URL

if not DATABASE_URL:
    DATABASE_URL = (
        f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

if DATABASE_URL.startswith("mysql://"):
    url_obj = make_url(DATABASE_URL)
    user = url_obj.username or ""
    password = url_obj.password or ""
    host = url_obj.host or "localhost"
    port = f":{url_obj.port}" if url_obj.port else ""
    database = f"/{url_obj.database}" if url_obj.database else ""

    DATABASE_URL = f"mysql+aiomysql://{user}:{password}@{host}{port}{database}"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


def get_user_schema(user: User) -> UserSchema:
    return UserSchema(
        id=user.id,
        email=user.email,
        access_token=user.access_token,
        apps_quota=user.apps_quota,
        services_quota=user.services_quota,
        networks_quota=user.networks_quota,
        apps=[app.name for app in user.apps],
        services=[service.name for service in user.services],
        networks=[network.name for network in user.networks],
        created_at=user.created_at,
        is_admin=user.is_admin,
        take_over_access_token=user.take_over_access_token,
        take_over_access_token_expiration=user.take_over_access_token_expiration,
    )


async def get_users() -> List[str]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()

    return [user.email for user in users]


async def get_user(email: str) -> UserSchema:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).options(*USER_EAGER_LOAD).filter_by(email=email)
        )
        user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_user_schema(user)


async def get_user_by_access_token(access_token: str) -> UserSchema:
    could_be_take_over = access_token.startswith("take-over")
    access_token = hash_access_token(access_token)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).options(*USER_EAGER_LOAD).filter_by(access_token=access_token)
        )
        user = result.scalar_one_or_none()

        if not user and could_be_take_over:
            now = datetime.datetime.now(datetime.timezone.utc)

            result = await db.execute(
                select(User)
                .options(*USER_EAGER_LOAD)
                .filter(
                    and_(
                        User.take_over_access_token == access_token,
                        User.take_over_access_token_expiration > now,
                    )
                )
            )
            user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid access token")

    return get_user_schema(user)


async def create_user(email: str, access_token: str) -> None:
    access_token = hash_access_token(access_token)
    validate_email_format(email)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).filter_by(email=email))

        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already exists")

        db_user = User(
            email=email,
            access_token=access_token,
        )
        db.add(db_user)

        await db.commit()
        await db.refresh(db_user)


async def update_user(email: str, user: UserSchema) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).options(*USER_EAGER_LOAD).filter_by(email=email)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_user.email = user.email
        db_user.is_admin = user.is_admin
        db_user.access_token = user.access_token
        db_user.apps_quota = user.apps_quota
        db_user.services_quota = user.services_quota
        db_user.networks_quota = user.networks_quota

        await db.commit()
        await db.refresh(db_user)


async def delete_user(email: str) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).filter_by(email=email))
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        await db.delete(db_user)
        await db.commit()


async def create_resource(email: str, name: str, resource_type: Type[Resource]) -> None:
    ResourceType = resource_type

    async with AsyncSessionLocal() as db:
        user_result = await db.execute(
            select(User).options(*USER_EAGER_LOAD).filter_by(email=email)
        )

        db_user = user_result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        existing_result = await db.execute(
            select(ResourceType).filter_by(name=name, user_email=email)
        )

        if existing_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Resource already exists")

        quota_map = {
            App: (db_user.apps_quota, db_user.apps),
            Service: (db_user.services_quota, db_user.services),
            Network: (db_user.networks_quota, db_user.networks),
        }
        quota, resources = quota_map.get(ResourceType)

        if quota <= len(resources):
            raise HTTPException(status_code=403, detail="Quota exceeded")

        resource = ResourceType(name=name, user_email=db_user.email)

        db.add(resource)

        await db.commit()
        await db.refresh(resource)


async def delete_resource(email: str, name: str, resource_type: Type[Resource]) -> None:
    async with AsyncSessionLocal() as db:
        user_result = await db.execute(select(User).filter_by(email=email))
        db_user = user_result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        resource_result = await db.execute(
            select(resource_type).filter_by(name=name, user_email=email)
        )
        resource = resource_result.scalar_one_or_none()

        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        await db.delete(resource)
        await db.commit()


async def get_app_by_deploy_token(deploy_token: str) -> Tuple[App, UserSchema]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(App)
            .options(selectinload(App.user).options(*USER_EAGER_LOAD))
            .filter_by(deploy_token=deploy_token)
        )
        app = result.scalar_one_or_none()

    if not app:
        raise HTTPException(status_code=404, detail="App does not exist")

    return app, get_user_schema(app.user)


async def get_app_deployment_token(name: str) -> str:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(App).filter_by(name=name))
        app = result.scalar_one_or_none()

    if not app:
        raise HTTPException(status_code=404, detail="App does not exist")

    return app.deploy_token


async def create_take_over_access_token(email: str) -> str:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).filter_by(email=email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        take_over_access_token = (
            f"take-over-{secrets.token_urlsafe(64)}-{int(time.time())}"
        )

        user.take_over_access_token = hash_access_token(take_over_access_token)
        user.take_over_access_token_expiration = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(days=1)

        await db.commit()
        await db.refresh(user)

    return take_over_access_token


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
