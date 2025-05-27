import secrets
from typing import List, Optional, Tuple, Type

from fastapi import HTTPException
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    select,
)
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, relationship, selectinload

from src.api.models.schema import UserSchema
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
        f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

if DATABASE_URL.startswith("mysql://"):
    url_obj = make_url(DATABASE_URL)
    user = url_obj.username or ""
    password = url_obj.password or ""
    host = url_obj.host or "localhost"
    port = f":{url_obj.port}" if url_obj.port else ""
    database = f"/{url_obj.database}" if url_obj.database else ""

    DATABASE_URL = f"mysql+asyncmy://{user}:{password}@{host}{port}{database}"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


def generate_token(size: int) -> str:
    return secrets.token_urlsafe(size)


class User(Base):
    __tablename__ = "user"

    email = Column(String(100), primary_key=True)
    access_token = Column(String(500), unique=True)
    apps_quota = Column(Integer, nullable=False, default=0)
    services_quota = Column(Integer, nullable=False, default=0)
    networks_quota = Column(Integer, nullable=False, default=0)
    storage_quota = Column(Integer, nullable=False, default=0)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    apps = relationship("App", back_populates="user", cascade="all, delete")
    services = relationship("Service", back_populates="user", cascade="all, delete")
    networks = relationship("Network", back_populates="user", cascade="all, delete")
    storages = relationship("Storage", back_populates="user", cascade="all, delete")


class Resource(Base):
    __abstract__ = True

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class App(Resource):
    __tablename__ = "app"
    name = Column(String(255), primary_key=True)
    deploy_token = Column(String(1024), nullable=True)

    user_email = Column(String(255), ForeignKey("user.email"))
    user = relationship("User", back_populates="apps", foreign_keys=[user_email])

    def __init__(
        self,
        name: str,
        deploy_token: Optional[str] = None,
        user_email: Optional[str] = None,
        created_at: Optional[DateTime] = None,
    ):
        self.name = name
        self.deploy_token = deploy_token
        self.user_email = user_email
        self.created_at = created_at

        if self.deploy_token is None:
            self.deploy_token = f"{name}-{generate_token(512)}"


class Service(Resource):
    __tablename__ = "service"
    name = Column(String(255), primary_key=True)

    user_email = Column(String(255), ForeignKey("user.email"))
    user = relationship("User", back_populates="services", foreign_keys=[user_email])


class Network(Resource):
    __tablename__ = "network"
    name = Column(String(255), primary_key=True)

    user_email = Column(String(255), ForeignKey("user.email"))
    user = relationship("User", back_populates="networks", foreign_keys=[user_email])


class Storage(Resource):
    __tablename__ = "storage"
    name = Column(String(255), primary_key=True)

    user_email = Column(String(255), ForeignKey("user.email"))
    user = relationship("User", back_populates="storages", foreign_keys=[user_email])


USER_EAGER_LOAD = [
    selectinload(User.apps),
    selectinload(User.services),
    selectinload(User.networks),
    selectinload(User.storages),
]


def get_user_schema(user: User) -> UserSchema:
    return UserSchema(
        email=user.email,
        access_token=user.access_token,
        apps_quota=user.apps_quota,
        services_quota=user.services_quota,
        networks_quota=user.networks_quota,
        storage_quota=user.storage_quota,
        apps=[app.name for app in user.apps],
        services=[service.name for service in user.services],
        networks=[network.name for network in user.networks],
        storages=[storage.name for storage in user.storages],
        created_at=user.created_at,
        is_admin=user.is_admin,
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
    access_token = hash_access_token(access_token)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).options(*USER_EAGER_LOAD).filter_by(access_token=access_token)
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
        db_user.storage_quota = user.storage_quota

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
            Storage: (db_user.storage_quota, db_user.storages),
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


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
