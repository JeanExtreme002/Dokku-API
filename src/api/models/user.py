from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship, selectinload

from src.api.models.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True)
    access_token = Column(String(500), unique=True)
    apps_quota = Column(Integer, nullable=False, default=0)
    services_quota = Column(Integer, nullable=False, default=0)
    networks_quota = Column(Integer, nullable=False, default=0)
    is_admin = Column(Boolean, nullable=False, default=False)
    take_over_access_token = Column(String(500), nullable=True, default=None)
    take_over_access_token_expiration = Column(
        DateTime(timezone=True), nullable=True, default=None
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    apps = relationship("App", back_populates="user", cascade="all, delete")
    services = relationship("Service", back_populates="user", cascade="all, delete")
    networks = relationship("Network", back_populates="user", cascade="all, delete")


USER_EAGER_LOAD = [
    selectinload(User.apps),
    selectinload(User.services),
    selectinload(User.networks),
]
