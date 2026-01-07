from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime
from services.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, ForeignKey("users.username"))
    symbol = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    side = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
