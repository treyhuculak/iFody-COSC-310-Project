from enum import Enum
from datetime import datetime 
from pydantic import BaseModel

class NotificationType(Enum):
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_PICKED_UP = "order_picked_up"
    ORDER_IN_TRANSIT = "order_in_transit"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"
    PAYMENT_FAILED = "payment_failed"

class NotificationBase(BaseModel):
    user_id: int
    type: NotificationType
    title: str
    message: str
    is_read: bool = False
    order_id: int

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    created_at: datetime