from typing import Optional

from fastapi import HTTPException
from src.backend.models.restaurant import RestaurantCreate
from src.backend.models.menu_item import MenuItemCreate
from src.backend.repositories.restaurant_repo import RestaurantRepository

class RestaurantController:
    def __init__(self) -> None:
        self.repo = RestaurantRepository()

    def get_restaurant_by_id(self, restaurant_id: int):
        return self.repo.get_restaurant_by_id(restaurant_id)

    def get_restaurants_by_owner(self, owner_id: int):
        return self.repo.get_restaurants_by_owner(owner_id)

    def get_restaurants_by_location(self, location: str):
        return self.repo.get_restaurants_by_location(location)

    def get_all_restaurants(self):
        return self.repo.get_all_restaurants()

    def create_restaurant(self, restaurant: RestaurantCreate):
        # TODO: Validate restaurant data (e.g., name not empty, delivery fee >= 0)
        # TODO: generate a unique ID for the new restaurant (if not handled by the repository)
        # TODO: Call the repository method to save the restaurant and return the result
        return self.repo.create_restaurant(restaurant.model_dump())

    def update_restaurant(self, restaurant_id: int, name=None, cuisine=None, delivery_fee=None, location=None):
        restaurant_data = {
            "name": name,
            "cuisine": cuisine,
            "delivery_fee": delivery_fee,
            "location": location
        }

        restaurant_data = {k: v for k, v in restaurant_data.items() if v is not None}
        if not restaurant_data:
            return {"error": "No data provided for update."}
        
        return self.repo.update_restaurant(restaurant_id, restaurant_data)

    def delete_restaurant(self, restaurant_id: int):
        return self.repo.delete_restaurant(restaurant_id)

    def get_menu_items_by_restaurant_id(self, restaurant_id: int):
        return self.repo.get_menu_items_by_restaurant(restaurant_id)

    # Menu item related methods
    def add_menu_item_to_restaurant(self, menu_item: MenuItemCreate, restaurant_id: int):
        restaurant = self.repo.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Note: Basic field validation (e.g., price > 0) is handled by the MenuItemCreate Pydantic model.
        # TODO: Add the restaurant_id to the menu item data before saving
        menu_item_data = menu_item.model_dump()
        menu_item_data["restaurant_id"] = restaurant_id
        # TODO: Call the repository method to save the menu item and return the result
        return self.repo.add_menu_item_to_restaurant(menu_item_data, restaurant_id)
        
    def update_menu_item_from_restaurant(self, restaurant_id: int, menu_item_id: int, name=None, description=None, price=None):
        menu_item_data = {
            "name": name,
            "description": description,
            "price": price
        }

        menu_item_data = {k: v for k, v in menu_item_data.items() if v is not None}
        if not menu_item_data:
            return {"error": "No data provided for update."}
        
        return self.repo.update_menu_item_from_restaurant(restaurant_id, menu_item_id, menu_item_data)

    def delete_menu_item_from_restaurant(self, restaurant_id: int, menu_item_id: int):
        return self.repo.delete_menu_item_from_restaurant(restaurant_id, menu_item_id)