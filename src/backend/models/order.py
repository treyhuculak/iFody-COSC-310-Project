from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.backend.models.order_item import OrderItem

class OrderBase(BaseModel):
    customer_id: int
    restaurant_id: int
    status: str
    total_price: float
    tax: float

class OrderCreate(OrderBase):
    customer_id: int
    restaurant_id: int
    status: str
    total_price: float
    tax: float
    order_items: Optional[List[OrderItem]] = None

class Order(OrderBase):
    id: int
    timestamp: datetime
    order_items: Optional[List[OrderItem]] = None