from pydantic import BaseModel, Field
#from src.backend.models.menu_item import MenuItem

class OrderItemBase(BaseModel):
    quantity: int = Field(..., gt=0)  # must be > 0
    item_id: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    price_at_purchase: float 
