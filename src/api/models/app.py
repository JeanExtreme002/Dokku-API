import secrets
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from src.api.models.resource import Resource


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
            self.deploy_token = f"{name}-{secrets.token_urlsafe(512)}"
