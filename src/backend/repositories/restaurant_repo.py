import json
from typing import List, Optional, Dict
from src.backend.models.restaurant import Restaurant
from src.backend.models.menu_item import MenuItem

class RestaurantRepository:
    RESTAURANT_FILE = 'data/restaurants.json'

    def __init__(self):
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
                json.load(f)
        except FileNotFoundError:
            # file doesn't exist, create it with an empty list
            with open(self.RESTAURANT_FILE, 'w') as f:
                json.dump([], f, indent=4)
        

    def get_restaurant_by_id(self, restaurant_id: int) -> Optional[dict]:
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
                data = json.load(f)
                for restaurant in data:
                    if restaurant['id'] == restaurant_id:
                        return restaurant
                return {"error": f"Restaurant with id {restaurant_id} not found."}
        except FileNotFoundError:
            return {"error": f"File {self.RESTAURANT_FILE} not found."}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}


    def get_restaurants_by_owner(self, owner_id: int) -> List[dict]:
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
                data = json.load(f)
                return [restaurant for restaurant in data if restaurant['owner_id'] == owner_id]
        except FileNotFoundError:
            print(f"File {self.RESTAURANT_FILE} not found.")
            return []
        except json.JSONDecodeError as e:
            return [{"error": f"Error decoding JSON: {e}"}]
        

    def get_restaurants_by_location(self, location: str) -> List[dict]:
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
                data = json.load(f)
                return [restaurant for restaurant in data if restaurant['location'].lower() == location.lower()]
        except FileNotFoundError:
            return [{"error": f"File {self.RESTAURANT_FILE} not found."}]
        except json.JSONDecodeError as e:
            return [{"error": f"Error decoding JSON: {e}"}]
        

    def get_all_restaurants(self) -> List[dict]:
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return [{"error": f"File {self.RESTAURANT_FILE} not found."}]
        except json.JSONDecodeError as e:
            return [{"error": f"Error decoding JSON: {e}"}]
        

    def create_restaurant(self, restaurant_data: dict) -> dict:
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
                data = json.load(f)
                new_id = max([restaurant['id'] for restaurant in data], default=0) + 1
                restaurant_data['id'] = new_id
                data.append(restaurant_data)
            with open(self.RESTAURANT_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            return restaurant_data
        except FileNotFoundError:
            # create a new file and store the restaurant data
            restaurant_data['id'] = 1
            with open(self.RESTAURANT_FILE, 'w') as f:
                json.dump([restaurant_data], f, indent=4)
            return restaurant_data
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}
        
    
    def update_restaurant(self, restaurant_id: int, restaurant_data: dict) -> Optional[dict]:
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
                data = json.load(f)
                for i, restaurant in enumerate(data):
                    if restaurant['id'] == restaurant_id:
                        data[i].update(restaurant_data)  # Update the existing restaurant data with the new data
                        with open(self.RESTAURANT_FILE, 'w') as f:
                            json.dump(data, f, indent=4)
                        return data[i]
                return {"error": f"Restaurant with id {restaurant_id} not found."}
        except FileNotFoundError:
            return {"error": f"File {self.RESTAURANT_FILE} not found."}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}
        
    
    def delete_restaurant(self, restaurant_id: int) -> dict:
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
                data = json.load(f)
                deleted_rest = {}
                new_data = []
                for restaurant in data:
                    if restaurant['id'] == restaurant_id:
                        deleted_rest = restaurant
                    else:
                        new_data.append(restaurant)
                
                if len(new_data) == len(data):
                    return {"error": f"Restaurant with id {restaurant_id} not found."}
                with open(self.RESTAURANT_FILE, 'w') as f:
                    json.dump(new_data, f, indent=4)
                return deleted_rest
        except FileNotFoundError:
            return {"error": f"File {self.RESTAURANT_FILE} not found."}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}
        
    
    def get_menu_items_by_restaurant(self, restaurant_id: int) -> List[dict]:
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
                data = json.load(f)
                for restaurant in data:
                    if restaurant['id'] == restaurant_id:
                        return restaurant.get('menu_items', [])
                return [{"error": f"Restaurant with id {restaurant_id} not found."}]
        except FileNotFoundError:
            return [{"error": f"File {self.RESTAURANT_FILE} not found."}]
        except json.JSONDecodeError as e:
            return [{"error": f"Error decoding JSON: {e}"}]
        

    def add_menu_item_to_restaurant(self, item_data: dict, restaurant_id: int) -> dict:
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
                data = json.load(f)
                for restaurant in data:
                    if restaurant['id'] == restaurant_id:
                        menu_items = restaurant.get('menu_items', [])
                        new_item_id = max(item['id'] for item in menu_items) + 1 if menu_items else 1
                        item_data['id'] = new_item_id
                        menu_items.append(item_data)
                        restaurant['menu_items'] = menu_items

                with open(self.RESTAURANT_FILE, 'w') as f:
                    json.dump(data, f, indent=4)
                return item_data
        except FileNotFoundError:
            return {"error": f"File {self.RESTAURANT_FILE} not found."}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}
        
    def update_menu_item_from_restaurant(self, restaurant_id: int, menu_item_id: int, item_data: dict) -> dict:
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
                data = json.load(f)
                for restaurant in data:
                    if restaurant['id'] == restaurant_id:
                        menu_items = restaurant.get('menu_items', [])
                        for i, item in enumerate(menu_items):
                            if item['id'] == menu_item_id:
                                menu_items[i].update(item_data)
                                with open(self.RESTAURANT_FILE, 'w') as f:
                                    json.dump(data, f, indent=4)
                                return menu_items[i]
                        return {"error": f"Menu item with id {menu_item_id} not found in restaurant {restaurant_id}."}
                return {"error": f"Restaurant with id {restaurant_id} not found."}
        except FileNotFoundError:
            return {"error": f"File {self.RESTAURANT_FILE} not found."}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}
        
    def delete_menu_item_from_restaurant(self, restaurant_id: int, menu_item_id: int) -> dict:
        try:
            with open(self.RESTAURANT_FILE, 'r') as f:
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
                            return {"error": f"Menu item with id {menu_item_id} not found in restaurant {restaurant_id}."}
                        restaurant['menu_items'] = new_menu_items
                        with open(self.RESTAURANT_FILE, 'w') as f:
                            json.dump(data, f, indent=4)
                        return deleted_item
                return {"error": f"Restaurant with id {restaurant_id} not found."}
        except FileNotFoundError:
            return {"error": f"File {self.RESTAURANT_FILE} not found."}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}