from sqlalchemy import Column, DateTime, Integer, String, func

from src.api.models.base import Base


class CommandHistory(Base):
    __tablename__ = "command_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    command = Column(String(2048), nullable=False)
    username = Column(String(100), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
