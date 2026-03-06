from pydantic import BaseModel, Field
from src.backend.models.menu_item import MenuItemBase

class OrderItemBase(MenuItemBase):
    quantity: int = Field(..., gt=0)  # must be > 0

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    item_id: int