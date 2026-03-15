import json
from typing import List, Optional
from fastapi import HTTPException

class RestaurantRepository:
    DEFAULT_FILE = 'data/restaurants.json'

    def __init__(self, file_path: Optional[str] = None) -> None:
        self.file_path = file_path or self.DEFAULT_FILE
        try:
            with open(self.file_path, 'r') as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # file doesn't exist or is corrupted, create/reset it with an empty list
            with open(self.file_path, 'w') as f:
                json.dump([], f, indent=4)

    def get_restaurant_by_id(self, restaurant_id: int) -> dict:
        '''
        Gets the restaurant with the specified ID from the JSON file. 
        Raises a 404 error if not found, or a 500 error if there is an issue with the JSON data.
        '''
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for restaurant in data:
                    if restaurant['id'] == restaurant_id:
                        return restaurant
                raise HTTPException(status_code=404, detail=f"Restaurant with id {restaurant_id} not found.")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Restaurant missing id field: {e}")

    def get_restaurants_by_owner(self, owner_id: int) -> List[dict]:
        '''
        Gets all restaurants owned by the specified owner ID from the JSON file. 
        Raises a 404 error if the file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        if owner_id is None or owner_id == 0:
            raise HTTPException(status_code=400, detail="Invalid owner_id provided.")
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                return [restaurant for restaurant in data if restaurant.get('owner_id',0) == owner_id]
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")

    def get_restaurants_by_location(self, location: str) -> List[dict]:
        '''
        Gets all restaurants in the specified location from the JSON file. 
        Raises a 404 error if the file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        location = location.strip().lower()
        if not location:
            raise HTTPException(status_code=400, detail="Invalid location provided.")
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                return [restaurant for restaurant in data if restaurant.get('location','').lower().strip() == location]
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")

    def filter_restaurants(self, cuisine: str = "", location: str = "", max_fee: float = 0) -> List[dict]:
        '''
        Filters restaurants based on the provided criteria (cuisine, location, max delivery fee).
        If a criterion is not provided (e.g., empty string for cuisine/location or 0 for max_fee), it will not be used as a filter. 
        Raises a 404 error if the file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        cuisine, location = cuisine.strip().lower(), location.strip().lower()
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                filtered = []
                for restaurant in data:
                    if cuisine and cuisine != restaurant.get('cuisine','').lower().strip():
                        continue
                    if location and location != restaurant.get('location','').lower().strip():
                        continue
                    if max_fee > 0 and restaurant.get('delivery_fee', float('inf')) > max_fee:
                        continue
                    filtered.append(restaurant)
                return filtered
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")

    def get_restaurants_by_partial_name(self, name: str) -> List[dict]:
        '''
        Gets all restaurants whose names contain the specified substring from the JSON file. 
        Raises a 404 error if the file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        name = name.strip().lower()
        if name is None or name == "":
            return self.get_all_restaurants()
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                restaurants = []
                for restaurant in data:
                    if name in restaurant.get('name', '').lower().strip():
                        restaurants.append(restaurant)
                return restaurants
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
            
    def get_all_restaurants(self) -> List[dict]:
        '''
        Gets all restaurants from the JSON file. 
        Raises a 404 error if the file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")

    def add_restaurant(self, restaurant_data: dict) -> dict:
        '''
        Adds a new restaurant to the JSON file. 
        The restaurant_data dict should contain all necessary fields except for 'id', which will be auto-generated.
        Raises a 404 error if the file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                new_id = max([restaurant['id'] for restaurant in data], default=0) + 1
                restaurant_data['id'] = new_id
                data.append(restaurant_data)
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return restaurant_data
        except FileNotFoundError:
            # create a new file and store the restaurant data
            restaurant_data['id'] = 1
            with open(self.file_path, 'w') as f:
                json.dump([restaurant_data], f, indent=4)
            return restaurant_data
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Restaurant missing id field: {e}")
    
    def update_restaurant(self, restaurant_id: int, restaurant_data: dict) -> dict:
        '''
        Updates the restaurant with the specified ID in the JSON file using the provided restaurant_data dict. 
        Only the fields present in restaurant_data will be updated; other fields will remain unchanged.
        Raises a 404 error if the restaurant or file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for i, restaurant in enumerate(data):
                    if restaurant['id'] == restaurant_id:
                        data[i].update(restaurant_data)  # Update the existing restaurant data with the new data
                        with open(self.file_path, 'w') as f:
                            json.dump(data, f, indent=4)
                        return data[i]
                raise HTTPException(status_code=404, detail=f"Restaurant with id {restaurant_id} not found.")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Restaurant missing id field: {e}")
    
    def delete_restaurant(self, restaurant_id: int) -> dict:
        '''
        Deletes the restaurant with the specified ID from the JSON file and returns the deleted restaurant data.
        Raises a 404 error if the restaurant or file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                deleted_rest = {}
                new_data = []
                for restaurant in data:
                    if restaurant['id'] == restaurant_id:
                        deleted_rest = restaurant
                    else:
                        new_data.append(restaurant)
                
                if len(new_data) == len(data):
                    raise HTTPException(status_code=404, detail=f"Restaurant with id {restaurant_id} not found.")
                with open(self.file_path, 'w') as f:
                    json.dump(new_data, f, indent=4)
                return deleted_rest
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Restaurant missing id field: {e}")
    
    def get_menu_items_by_restaurant(self, restaurant_id: int) -> List[dict]:
        '''
        Gets all menu items for the restaurant with the specified ID from the JSON file. 
        Raises a 404 error if the restaurant or file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        try:
            restaurant = self.get_restaurant_by_id(restaurant_id)
            return restaurant.get('menu_items', [])
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Restaurant missing id field: {e}")

    def get_menu_item_by_partial_name(self, restaurant_id: int, name: str) -> List[dict]:
        '''
        Gets all menu items for the specified restaurant whose names contain the specified substring from the JSON file. 
        Raises a 404 error if the restaurant or file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        name = name.strip().lower()
        if name is None or name == "":
            return self.get_menu_items_by_restaurant(restaurant_id)
        try:
            menu_items = self.get_menu_items_by_restaurant(restaurant_id)
            return [item for item in menu_items if name in item.get('name', '').lower().strip()]
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Restaurant missing id field: {e}")
        
    def filter_menu_items(self, restaurant_id: int, max_price: float) -> List[dict]:
        '''
        Returns all menu items for the specified restaurant that have a price less than or equal to the specified max_price from the JSON file. 
        Raises a 404 error if the restaurant or file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        try:
            menu_items = self.get_menu_items_by_restaurant(restaurant_id)
            return [item for item in menu_items if item.get('price', float('inf')) <= max_price]
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Restaurant missing id field: {e}")

    def add_menu_item_to_restaurant(self, item_data: dict, restaurant_id: int) -> dict:
        '''
        Adds a new menu item to the specified restaurant in the JSON file. 
        The item_data dict should contain all necessary fields except for 'id', which will be auto-generated.
        Raises a 404 error if the restaurant or file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for restaurant in data:
                    if restaurant['id'] == restaurant_id:
                        menu_items = restaurant.get('menu_items', [])
                        new_item_id = max(item['id'] for item in menu_items) + 1 if menu_items else 1
                        item_data['id'] = new_item_id
                        menu_items.append(item_data)
                        restaurant['menu_items'] = menu_items

                with open(self.file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                return item_data
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Menu item missing id field: {e}")
        
    def update_menu_item_from_restaurant(self, restaurant_id: int, menu_item_id: int, item_data: dict) -> dict:
        '''
        Updates the menu item with the specified ID for the specified restaurant in the JSON file using the provided item_data dict.
        Only the fields present in item_data will be updated; other fields will remain unchanged.
        Raises a 404 error if the restaurant, menu item, or file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for restaurant in data:
                    if restaurant['id'] == restaurant_id:
                        menu_items = restaurant.get('menu_items', [])
                        for i, item in enumerate(menu_items):
                            if item['id'] == menu_item_id:
                                menu_items[i].update(item_data)
                                with open(self.file_path, 'w') as f:
                                    json.dump(data, f, indent=4)
                                return menu_items[i]
                        raise HTTPException(status_code=404, detail=f"Menu item with id {menu_item_id} not found in restaurant {restaurant_id}.")
                raise HTTPException(status_code=404, detail=f"Restaurant with id {restaurant_id} not found.")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Menu item missing id field: {e}")
        
    def delete_menu_item_from_restaurant(self, restaurant_id: int, menu_item_id: int) -> dict:
        '''
        Deletes the menu item with the specified ID from the specified restaurant in the JSON file and returns the deleted menu item data.
        Raises a 404 error if the restaurant, menu item, or file is not found, or a 500 error if there is an issue with the JSON data.
        '''
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for restaurant in data:
                    if restaurant['id'] == restaurant_id:
                        menu_items = restaurant.get('menu_items', [])
                        new_menu_items = []
                        deleted_item = {}
                        for item in menu_items:
                            if item['id'] == menu_item_id:
                                deleted_item = item
                            else:
                                new_menu_items.append(item)
                        if not deleted_item:
                            raise HTTPException(status_code=404, detail=f"Menu item with id {menu_item_id} not found in restaurant {restaurant_id}.")

                        if not new_menu_items:
                            # If no menu items remain, we might want to set the restaurant as unavailable
                            restaurant['is_available'] = False

                        restaurant['menu_items'] = new_menu_items
                        with open(self.file_path, 'w') as f:
                            json.dump(data, f, indent=4)
                        return deleted_item
                raise HTTPException(status_code=404, detail=f"Restaurant with id {restaurant_id} not found.")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Menu item missing id field: {e}")
        
    
        