from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.api.models.resource import Resource


class Network(Resource):
    __tablename__ = "network"
    name = Column(String(255), primary_key=True)

    user_email = Column(String(255), ForeignKey("user.email"))
    user = relationship("User", back_populates="networks", foreign_keys=[user_email])
