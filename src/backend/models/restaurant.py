from pydantic import BaseModel, Field
from typing import List, Optional

from src.backend.models.menu_item import MenuItem

class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=1)  # Name must not be empty
    cuisine: str = Field(..., min_length=1)  # Cuisine must not be empty
    location: str = Field(..., min_length=1)  # Location must not be empty
    delivery_fee: float = Field(..., ge=0)  # Delivery fee must be greater than or equal to 0

class RestaurantCreate(RestaurantBase):
    owner_id: Optional[int] = None

class Restaurant(RestaurantBase):
    id: int
    owner_id: int
    menu_items: List[MenuItem] = Field(default_factory=list)
