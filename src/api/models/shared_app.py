from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship

from src.api.models.base import Base


class SharedApp(Base):
    __tablename__ = "shared_app"
    app_name = Column(String(255), ForeignKey("app.name"), primary_key=True)
    user_email = Column(String(100), ForeignKey("user.email"), primary_key=True)

    pretty_app_name = Column(String(255), nullable=False)
    author_email = Column(String(100), nullable=False)

    shared_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    app = relationship("App", back_populates="shared_users")
    user = relationship("User", back_populates="shared_apps")
