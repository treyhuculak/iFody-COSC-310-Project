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

class OrderLocation(Enum):
    BRITISH_COLUMBIA = "BC"
    ALBERTA = "AB"
    SASKATCHEWAN = "SK"
    MANITOBA = "MB"
    ONTARIO = "ON"
    QUEBEC = "QC"
    NEW_BRUNSWICK = "NB"
    NOVA_SCOTIA = "NS"
    PRINCE_EDWARD_ISLAND = "PE"
    NEWFOUNDLAND_AND_LABRADOR = "NL"
    YUKON = "YT"
    NORTHWEST_TERRITORIES = "NT"
    NUNAVUT = "NU"

class OrderBase(BaseModel):
    customer_id: int
    restaurant_id: int
    status: OrderStatus = OrderStatus.PENDING
    location: OrderLocation = OrderLocation.BRITISH_COLUMBIA
    order_items: List[OrderItem] = []

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    timestamp: datetime
    subtotal_price: float
    total_price: float
    tax: float
    delivery_fee: float
