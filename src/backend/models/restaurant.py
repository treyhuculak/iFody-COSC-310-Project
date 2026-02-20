from pydantic import BaseModel, Field
from typing import List, Optional

from src.backend.models.menu_item import MenuItem

class RestaurantBase(BaseModel):
    name: str
    cuisine: str
    location: str
    delivery_fee: float = Field(..., ge=0)  # Delivery fee must be greater than or equal to 0
    owner_id: int

class RestaurantCreate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    id: int
    menu_items: List[MenuItem] = []
