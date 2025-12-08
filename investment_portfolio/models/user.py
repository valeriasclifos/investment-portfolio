from sqlalchemy import Column, String, Float
from services.database import Base


class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
