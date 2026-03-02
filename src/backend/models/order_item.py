from pydantic import BaseModel, Field

class OrderItemBase(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0)  # must be > 0

class OrderItem(OrderItemBase):
    order_id: int
    subtotal: float
