from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import declarative_base
from sqlalchemy import Enum as SQLEnum
from app.enums import OrderStatus
import datetime

Base = declarative_base()
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    order_type = Column(String(10), nullable=False)
    status = Column(
        SQLEnum(OrderStatus, name="order_status"),  # 明确指定枚举名称
        default=OrderStatus.PENDING
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)