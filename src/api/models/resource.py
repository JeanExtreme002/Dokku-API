from sqlalchemy import Column, DateTime, func

from src.api.models.base import Base


class Resource(Base):
    __abstract__ = True

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
