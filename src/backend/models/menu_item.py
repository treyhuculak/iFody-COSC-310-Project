from typing import List, Optional
from pydantic import BaseModel, Field

class MenuItemBase(BaseModel):
    name: str
    description: str
    price: float = Field(..., gt=0)  # Price must be greater than 0

class MenuItemCreate(MenuItemBase):
    pass

class MenuItem(MenuItemBase):
    id: int
