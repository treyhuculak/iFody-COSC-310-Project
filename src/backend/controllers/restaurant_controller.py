from typing import Optional

from fastapi import HTTPException
from src.backend.models.restaurant import RestaurantCreate, Restaurant
from src.backend.models.menu_item import MenuItem, MenuItemCreate
from src.backend.models.pagination import PaginatedResponse
from src.backend.repositories.restaurant_repo import RestaurantRepository

class RestaurantController:
    def __init__(self, repo: Optional[RestaurantRepository] = None) -> None:
        self.repo = repo or RestaurantRepository()

    def _build_paginated_response(self, items: list, total: int, 
                                  skip: int, limit: int) -> PaginatedResponse:
        total_pages = (total + limit - 1) // limit
        return PaginatedResponse(
            items=items,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            total_pages=total_pages,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )

    '''
    Restaurant operations:
        - Get a restaurant by ID
        - Get restaurants by owner ID
        - Get restaurants by location
        - Filter restaurants by cuisine, location, and max delivery fee
        - Get restaurants by partial name match
        - Get all restaurants
        - Create a restaurant
        - Update a restaurant
        - Delete a restaurant
        - Get menu items for a restaurant
    '''
    def get_restaurant_by_id(self, restaurant_id: int):
        restaurant = self.repo.get_restaurant_by_id(restaurant_id)
        return Restaurant(**restaurant)

    def get_restaurants_by_owner(self, owner_id: int, skip: int = 0, limit: int = 10) -> PaginatedResponse:
        owner_restaurants, total = self.repo.get_restaurants_by_owner(owner_id, skip, limit)
        response_restaurants = [Restaurant(**r) for r in owner_restaurants]
        return self._build_paginated_response(response_restaurants, total, skip, limit)

    def get_restaurants_by_location(self, location: str, skip: int = 0, limit: int = 10) -> PaginatedResponse:
        location_restaurants, total = self.repo.get_restaurants_by_location(location, skip, limit)
        response_restaurants = [Restaurant(**r) for r in location_restaurants]
        return self._build_paginated_response(response_restaurants, total, skip, limit)

    def filter_restaurants(self, cuisine: str = "", location: str = "", max_fee: float = 0, 
                           skip: int = 0, limit: int = 10) -> PaginatedResponse:
        restaurants, total = self.repo.filter_restaurants(cuisine=cuisine, location=location, max_fee=max_fee, skip=skip, limit=limit)
        response_restaurants = [Restaurant(**r) for r in restaurants]
        return self._build_paginated_response(response_restaurants, total, skip, limit)

    def get_restaurants_by_partial_name(self, partial_name: str, 
                                        skip: int = 0, limit: int = 10) -> PaginatedResponse:
        matching_restaurants, total = self.repo.get_restaurants_by_partial_name(partial_name, skip=skip, limit=limit)
        response_restaurants = [Restaurant(**r) for r in matching_restaurants]
        return self._build_paginated_response(response_restaurants, total, skip, limit)

    def get_all_restaurants(self, skip: int = 0, limit: int = 10) -> PaginatedResponse:
        all_restaurants, total = self.repo.get_all_restaurants(skip=skip, limit=limit)
        response_restaurants = [Restaurant(**r) for r in all_restaurants]
        return self._build_paginated_response(response_restaurants, total, skip, limit)

    def add_restaurant(self, restaurant: RestaurantCreate, owner_id: int = 1) -> Restaurant:
        restaurant_data = restaurant.model_dump()
        # Always use the authenticated owner's ID; ignore any owner_id from the request body
        restaurant_data['owner_id'] = owner_id
        added_restaurant = self.repo.add_restaurant(restaurant_data)
        return Restaurant(**added_restaurant)

    def update_restaurant(self, restaurant_id: int, name=None, cuisine=None, delivery_fee=None, location=None, is_available=None):
        restaurant_data = {
            "name": name,
            "cuisine": cuisine,
            "location": location,
            "delivery_fee": delivery_fee,
            "is_available": is_available
        }
        # Remove keys with None values to avoid overwriting existing data with None
        restaurant_data = {k: v for k, v in restaurant_data.items() if v is not None}
        if not restaurant_data:
            raise HTTPException(status_code=400, detail="No data provided for update.")
        
        # Block marking restaurant as available if it has no menu items
        if "is_available" in restaurant_data and restaurant_data["is_available"] == True:
            # Check if the restaurant has menu items before allowing it to be marked as available
            menu_items, total = self.repo.get_menu_items_by_restaurant(restaurant_id)

            if total == 0:
                raise HTTPException(status_code=400, detail="Cannot mark restaurant as available without menu items.")
        
        updated_restaurant = self.repo.update_restaurant(restaurant_id, restaurant_data)
        return Restaurant(**updated_restaurant)

    def delete_restaurant(self, restaurant_id: int):
        deleted_restaurant = self.repo.delete_restaurant(restaurant_id)
        return Restaurant(**deleted_restaurant)

    def get_menu_items_by_restaurant_id(self, restaurant_id: int, skip: int = 0, limit: int = 10) -> PaginatedResponse:
        all_menu_items, total = self.repo.get_menu_items_by_restaurant(restaurant_id, skip, limit)
        response_menu_items = [MenuItem(**item) for item in all_menu_items]
        return self._build_paginated_response(response_menu_items, total, skip, limit)

    '''
    Menu item operations for a specific restaurant:
        - Get menu items by partial name match
        - Filter menu items by max price
        - Add a menu item to a restaurant
        - Update a menu item from a restaurant
        - Delete a menu item from a restaurant
    '''
    def get_menu_items_by_partial_name(self, restaurant_id: int, partial_name: str, skip: int = 0, limit: int = 10) -> PaginatedResponse:
        menu_items, total = self.repo.get_menu_item_by_partial_name(restaurant_id, partial_name, skip, limit)
        return self._build_paginated_response(menu_items, total, skip, limit)

    def filter_menu_items(self, restaurant_id: int, max_price: float, skip: int = 0, limit: int = 10) -> PaginatedResponse:
        menu_items, total = self.repo.filter_menu_items(restaurant_id, max_price, skip, limit)
        return self._build_paginated_response(menu_items, total, skip, limit)

    def add_menu_item_to_restaurant(self, menu_item: MenuItemCreate, restaurant_id: int):
        restaurant = self.repo.get_restaurant_by_id(restaurant_id)
        if isinstance(restaurant, dict) and "error" in restaurant:
            raise HTTPException(status_code=404, detail=restaurant["error"])
        
        # Note: Basic field validation (e.g., price > 0) is handled by the MenuItemCreate Pydantic model.
        menu_item_data = menu_item.model_dump()
        added_item = self.repo.add_menu_item_to_restaurant(menu_item_data, restaurant_id)
        return MenuItem(**added_item)
        
    def update_menu_item_from_restaurant(self, restaurant_id: int, menu_item_id: int, name=None, description=None, price=None):
        menu_item_data = {
            "name": name,
            "description": description,
            "price": price
        }

        menu_item_data = {k: v for k, v in menu_item_data.items() if v is not None}
        if not menu_item_data:
            raise HTTPException(status_code=400, detail="No data provided for update.")
        
        updated_item = self.repo.update_menu_item_from_restaurant(restaurant_id, menu_item_id, menu_item_data)
        return MenuItem(**updated_item)

    def delete_menu_item_from_restaurant(self, restaurant_id: int, menu_item_id: int):
        deleted_item = self.repo.delete_menu_item_from_restaurant(restaurant_id, menu_item_id)
        return MenuItem(**deleted_item) 