from pydantic import BaseModel
from typing import Optional
from datetime import datetime

'''
Instead of having a delivery status field we are going to use the order status field so no overlap between the two happens
This way we do not need to worry about the same order and the delivery being in different states
Therefore, the purpose of this class is just to keep track of the delivery variables (driver, and all time parameters) -> This way we don't overpopulate the order class
'''

class DeliveryBase(BaseModel):
    order_id: int

class DeliveryCreate(DeliveryBase):
    pass

class Delivery(DeliveryBase):
    id: int
    driver_id: int # -> I'm not really sure if we need this field at all since we r not dealing with the driver perspective
    assigned_at: datetime
    estimated_delivery_time: datetime
    delivered_at: Optional[datetime] = None