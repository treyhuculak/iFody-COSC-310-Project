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
        pass

    def get_all_restaurants(self):
        return self.repo.get_all_restaurants()

    def create_restaurant(self, restaurant: RestaurantCreate):
        # TODO: Validate restaurant data (e.g., name not empty, delivery fee >= 0)
        # TODO: generate a unique ID for the new restaurant (if not handled by the repository)
        # TODO: Call the repository method to save the restaurant and return the result
        pass

    def update_restaurant(self, restaurant_id: int, name: str, status: str, delivery_fee: float, location: str):
        pass

    def delete_restaurant(self, restaurant_id: int):
        pass

    def get_menu_items_by_restaurant_id(self, restaurant_id: int):
        pass

    # Menu item related methods
    def add_menu_item_to_restaurant(self, menu_item: MenuItemCreate, restaurant_id: int):
        restaurant = self.repo.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Note: Basic field validation (e.g., price > 0) is handled by the MenuItemCreate Pydantic model.
        # TODO: Add the restaurant_id to the menu item data before saving
        # TODO: Call the repository method to save the menu item and return the result
        pass

