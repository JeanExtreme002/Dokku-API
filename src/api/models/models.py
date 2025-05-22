from typing import Type

from fastapi import HTTPException
from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String, create_engine)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from src.api.models.user import UserSchema
from src.config import Config

DB_USER = Config.DATABASE.DB_USER
DB_PASSWORD = Config.DATABASE.DB_PASSWORD
DB_HOST = Config.DATABASE.HOST
DB_PORT = Config.DATABASE.PORT
DB_NAME = Config.DATABASE.DB_NAME

DATABASE_URL = Config.DATABASE.DB_URL

if not DATABASE_URL:
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    email = Column(String(255), primary_key=True)
    access_token = Column(String(1024), nullable=True)
    apps_quote = Column(Integer, nullable=False, default=0)
    services_quote = Column(Integer, nullable=False, default=0)
    networks_quote = Column(Integer, nullable=False, default=0)
    storage_quote = Column(Integer, nullable=False, default=0)
    isAdmin = Column(Boolean, nullable=False, default=False)

    apps = relationship("App", backref="user", cascade="all, delete")
    services = relationship("Service", backref="user", cascade="all, delete")
    networks = relationship("Network", backref="user", cascade="all, delete")
    storages = relationship("Storage", backref="user", cascade="all, delete")


class Resource(Base):
    __abstract__ = True
    user_email = Column(String(255), ForeignKey("user.email"))


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


def get_user(email: str) -> UserSchema:
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserSchema(
        email=user.email,
        access_token=user.access_token,
        apps_quote=user.apps_quote,
        services_quote=user.services_quote,
        networks_quote=user.networks_quote,
        storage_quote=user.storage_quote,
        apps=[app.name for app in user.apps],
        services=[service.name for service in user.services],
        networks=[network.name for network in user.networks],
        storages=[storage.name for storage in user.storages],
    )


def create_user(email: str, access_token: str) -> None:
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


def update_user(email: str, user: UserSchema):
    db = SessionLocal()
    db_user = db.query(User).filter_by(email=email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.access_token = user.access_token
    db_user.apps_quote = user.apps_quote
    db_user.services_quote = user.services_quote
    db_user.networks_quote = user.networks_quote
    db_user.storage_quote = user.storage_quote

    db.commit()
    return get_user(email)


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
