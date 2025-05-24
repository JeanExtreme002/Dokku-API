from typing import List, Type

from fastapi import HTTPException
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
)
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from src.api.models.schema import UserSchema
from src.api.tools import validate_email_format
from src.config import Config

DB_USER = Config.DATABASE.DB_USER
DB_PASSWORD = Config.DATABASE.DB_PASSWORD
DB_HOST = Config.DATABASE.HOST
DB_PORT = Config.DATABASE.PORT
DB_NAME = Config.DATABASE.DB_NAME

DATABASE_URL = Config.DATABASE.DB_URL

if not DATABASE_URL:
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

if DATABASE_URL.startswith("mysql://"):
    url_obj = make_url(DATABASE_URL)
    user = url_obj.username or ""
    password = url_obj.password or ""
    host = url_obj.host or "localhost"
    port = f":{url_obj.port}" if url_obj.port else ""
    database = f"/{url_obj.database}" if url_obj.database else ""

    DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}{port}{database}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    email = Column(String(255), primary_key=True)
    access_token = Column(String(1024), nullable=True)
    apps_quota = Column(Integer, nullable=False, default=0)
    services_quota = Column(Integer, nullable=False, default=0)
    networks_quota = Column(Integer, nullable=False, default=0)
    storage_quota = Column(Integer, nullable=False, default=0)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    apps = relationship("App", backref="user", cascade="all, delete")
    services = relationship("Service", backref="user", cascade="all, delete")
    networks = relationship("Network", backref="user", cascade="all, delete")
    storages = relationship("Storage", backref="user", cascade="all, delete")


class Resource(Base):
    __abstract__ = True
    user_email = Column(String(255), ForeignKey("user.email"))
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class App(Resource):
    __tablename__ = "app"
    name = Column(String(255), primary_key=True)


class Service(Resource):
    __tablename__ = "service"
    name = Column(String(255), primary_key=True)


class Network(Resource):
    __tablename__ = "network"
    name = Column(String(255), primary_key=True)


class Storage(Resource):
    __tablename__ = "storage"
    name = Column(String(255), primary_key=True)


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


def get_users() -> List[str]:
    db = SessionLocal()
    users = db.query(User).all()

    return [user.email for user in users]


def get_user(email: str) -> UserSchema:
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_user_schema(user)


def get_user_by_access_token(access_token: str) -> UserSchema:
    db = SessionLocal()
    user = db.query(User).filter_by(access_token=access_token).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid access token")

    return get_user_schema(user)


def create_user(email: str, access_token: str) -> None:
    validate_email_format(email)

    db = SessionLocal()

    if db.query(User).filter_by(email=email).first():
        raise HTTPException(status_code=400, detail="User already exists")

    db_user = User(
        email=email,
        access_token=access_token,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


def update_user(email: str, user: UserSchema) -> None:
    db = SessionLocal()
    db_user = db.query(User).filter_by(email=email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.email = user.email
    db_user.is_admin = user.is_admin
    db_user.access_token = user.access_token
    db_user.apps_quota = user.apps_quota
    db_user.services_quota = user.services_quota
    db_user.networks_quota = user.networks_quota
    db_user.storage_quota = user.storage_quota

    db.commit()
    db.refresh(db_user)


def delete_user(email: str) -> None:
    db = SessionLocal()
    db_user = db.query(User).filter_by(email=email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()


def create_resource(email: str, name: str, resource_type: Type[Resource]) -> None:
    ResourceType = resource_type

    db = SessionLocal()
    db_user = db.query(User).filter_by(email=email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db.query(ResourceType).filter_by(name=name, user_email=email).first():
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

    resource = ResourceType(name=name, user_email=email)

    db.add(resource)
    db.commit()
    db.refresh(resource)


def delete_resource(email: str, name: str, resource_type: Type[Resource]) -> None:
    db = SessionLocal()
    db_user = db.query(User).filter_by(email=email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    resource = db.query(resource_type).filter_by(name=name, user_email=email).first()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    db.delete(resource)
    db.commit()


Base.metadata.create_all(bind=engine)
