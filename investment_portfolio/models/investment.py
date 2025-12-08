from sqlalchemy import Column, Integer, Float, String, ForeignKey
from services.database import Base


class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, ForeignKey("users.username"))
    symbol = Column(String)
    quantity = Column(Integer)
    avg_buy_price = Column(Float)
