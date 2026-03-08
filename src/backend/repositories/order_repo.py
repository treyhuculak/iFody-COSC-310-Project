import json
from typing import List, Optional, Dict
from datetime import datetime
from fastapi import HTTPException

class OrderRepository:
    ORDER_FILE = 'data/order.json'

    def __init__(self, file_path: Optional[str] = None) -> None:
        # check if files exist, if not create them with headers
        self.file_path = file_path or self.ORDER_FILE
        try:
            with open(self.file_path, 'r') as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # file doesn't exist or is corrupted, create/reset it with an empty list
            with open(self.file_path, 'w') as f:
                json.dump([], f, indent=4)
        pass
    
    def get_order_by_id(self, order_id: int) -> Optional[dict]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                # Getting the first order that matches the provided order_id 
                order = next(filter(lambda order: order.get("id") == order_id, data), None)
                return order
                    
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Order missing id field: {e}")
    

    def create_order(self, order_data: dict) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)

                # Creating new order id based on last order added to order_data
                new_id = max([order['id'] for order in data], default=0) + 1
                order_data['id'] = new_id
                order_data["timestamp"] = datetime.now().isoformat()

                data.append(order_data)
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return order_data

        except FileNotFoundError:
            # create a new file and store the order data
            order_data['id'] = 1
            with open(self.file_path, 'w') as f:
                json.dump([order_data], f, indent=4)
            return order_data
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Order missing id field: {e}")
    
    def delete_order(self, order_id: int) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                new_data = data.copy()
                deleted_order = None
                
                # Iterating data to find the order key and then deleting it from new_data
                for k, order in enumerate(data):
                    if order["id"] == order_id:
                        deleted_order = new_data.pop(k)
                        break
                
                # If nothing is found
                if deleted_order == None:
                    raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found.")
                
                # Saving changes
                with open(self.file_path, 'w') as f:
                    json.dump(new_data, f, indent=4)

                return deleted_order
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Order missing id field: {e}")
        
    def update_order_status(self, order_id: int, order_status: str) -> Optional[dict]:
        with open(self.file_path, 'r') as j:
            data = json.load(j)
            for i, order in enumerate(data):
                if order["id"] == order_id:
                    order["status"] = order_status
                    with open(self.file_path, 'w') as f:
                        json.dump(data, f, indent=4)
                    return order 
        return None
                
    def add_order_item_to_order(self, item_data: dict, order_id: int, price: float) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                flag = True

                # Iterate across all orders
                for order in data:
                    if order['id'] == order_id:
                        order_items = order.get('order_items', [])

                        # Look if the order item already exists in order items (find the first match)
                        order_item = next(filter(lambda item: item["item_id"] == item_data["item_id"], order_items), None)

                        # Adding order_id and price_at_purchase fields to order item
                        item_data["order_id"] = order_id
                        item_data["price_at_purchase"] = price

                        # If nothing is found, add new item. Else: increase item quantity
                        if order_item == None:
                            order_items.append(item_data)
                            order['order_items'] = order_items
                        else:
                            order_item["quantity"] += item_data["quantity"]

                        flag = False
                        break
                
                # Ensure a correct error message appears if order id is not found
                if flag:
                    raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found.")
                
                with open(self.file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                return order_item if order_item != None else item_data
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Order item missing id field: {e}")
        
    def delete_order_item_from_order(self, order_id: int, order_item_id: int):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                flag = True

                # Iterate across all orders
                for order in data:
                    if order['id'] == order_id:
                        order_items = order.get('order_items', [])
                        new_order_items = order_items.copy()
                        deleted_item = None

                        # Decrease item quantity. If item quantity reaches 0 -> Delete order item as a whole
                        for k, item in enumerate(order_items):
                            if item["item_id"] == order_item_id:
                                if new_order_items[k]["quantity"] <= 1:
                                    deleted_item = new_order_items.pop(k)
                                else:
                                    new_order_items[k]["quantity"] -= 1
                                    deleted_item = new_order_items[k]

                                flag = False
                                break
                        
                        # Ensure a correct error message appears if order item id is not found
                        if deleted_item == None:
                            raise HTTPException(status_code=404, detail=f"Order item with id {order_item_id} not found.")
                        
                        order["order_items"] = new_order_items
                        
                        with open(self.file_path, 'w') as f:
                            json.dump(data, f, indent=4)
                        return deleted_item
                
                # Ensure a correct error message appears if order id is not found
                if flag:
                    raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found.")
                
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Order item missing id field: {e}")
        
    def get_order_items_from_order(self, order_id: int) -> List[dict]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for order in data:
                    if order['id'] == order_id:
                        return order.get('order_items', [])
                raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found.")
            
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Order item missing id field: {e}")
                    
