from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.api.models.base import (
    USER_EAGER_LOAD,
    App,
    Base,
    Network,
    Resource,
    Service,
    SharedApp,
    User,
)
from src.api.schemas import UserSchema
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


async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
