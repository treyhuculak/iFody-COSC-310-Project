import csv
from typing import List, Optional, Dict
from src.backend.models.restaurant import Restaurant
from src.backend.models.menu_item import MenuItem

class RestaurantRepository:
    RESTAURANT_FILE = 'data/restaurants.csv'
    MENU_ITEM_FILE = 'data/menu_items.csv'

    def __init__(self):
        # check if files exist, if not create them with headers
        pass

    def get_restaurant_by_id(self, restaurant_id: int) -> Optional[dict]:
        return None

    def get_restaurants_by_owner(self, owner_id: int) -> List[dict]:
        return []

    def get_restaurants_by_location(self, location: str) -> List[dict]:
        return []

    def get_all_restaurants(self) -> List[dict]:
        return []

    def create_restaurant(self, restaurant_data: dict) -> dict:
        return {}
    
    def update_restaurant(self, restaurant_data: dict) -> Optional[dict]:
        return None
    
    def delete_restaurant(self, restaurant_id: int) -> bool:
        return False
    
    def get_menu_items_by_restaurant(self, restaurant_id: int) -> List[dict]:
        return []
    
    def add_menu_item_to_restaurant(self, item_data: dict) -> dict:
        return {}