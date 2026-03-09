from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.backend.models.order_item import OrderItem
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    AWAITING_PAYMENT = "awaiting payment"
    PAYMENT_CONFIRMED = "payment confirmed"
    PREPARING_ORDER = "preparing"
    OUT_FOR_DELIVERY = "out for delivery"
    DELIVERED = "delivered"
    PAYMENT_FAILED = "payment failed"


class OrderBase(BaseModel):
    customer_id: int
    restaurant_id: int
    status: OrderStatus
    total_price: float
    tax: float

class OrderCreate(OrderBase):
    order_items: Optional[List[OrderItem]] = None

class Order(OrderBase):
    id: int
    timestamp: datetime
    order_items: Optional[List[OrderItem]] = None

    def calculate_total(self):
        pass
