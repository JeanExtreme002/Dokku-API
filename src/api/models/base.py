from sqlalchemy.orm import declarative_base

Base = declarative_base()

from src.api.models.app import App
from src.api.models.network import Network
from src.api.models.resource import Resource
from src.api.models.service import Service
from src.api.models.user import USER_EAGER_LOAD, User
