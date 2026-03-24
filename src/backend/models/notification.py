from enum import Enum
from datetime import datetime 
from typing import Optional
from pydantic import BaseModel

class NotificationType(Enum):
    ORDER_CONFIRMED = "order confirmed"
    ORDER_IN_TRANSIT = "order in transit"
    ORDER_DELIVERED = "order delivered"
    ORDER_CANCELLED = "order cancelled"
    PAYMENT_FAILED = "payment failed"
    ORDER_IN_PROGRESS = "order in progress"
    NEW_ORDER_RECEIVED = "new order received"
    ORDER_FAILED = "order has failed to complete"
    NEW_ITEM_ADDED = "new item has been added to order"
    BLOCKED_ACCOUNT = "your account has been blocked"
    UNLBOCKED_ACCOUNT = "your account is now unblocked"

class NotificationBase(BaseModel):
    user_id: int
    type: NotificationType
    title: str
    message: str
    is_read: bool = False
    order_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    created_at: datetime