from pydantic import BaseModel, Field
#from src.backend.models.menu_item import MenuItem

class OrderItemBase(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0)  # must be > 0

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    order_id: int
    subtotal: float
