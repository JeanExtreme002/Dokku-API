from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.api.models.resource import Resource


class Service(Resource):
    __tablename__ = "service"
    name = Column(String(255), primary_key=True)

    user_email = Column(String(255), ForeignKey("user.email"))
    user = relationship("User", back_populates="services", foreign_keys=[user_email])
