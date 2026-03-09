from enum import Enum
from datetime import datetime 
from pydantic import BaseModel

class NotificationType(Enum):
    ORDER_CONFIRMED = "order confirmed"
    ORDER_IN_TRANSIT = "order in transit"
    ORDER_DELIVERED = "order delivered"
    ORDER_CANCELLED = "order cancelled"
    PAYMENT_FAILED = "payment failed"
    ORDER_IN_PROGRESS = "order in progress"
    NEW_ORDER_RECEIVED = "new order received"

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