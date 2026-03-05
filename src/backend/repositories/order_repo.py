import json
from typing import List, Optional, Dict
from datetime import datetime


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
            return {"error": f"File {self.file_path} not found."}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}
        except KeyError as e:
            return {"error": f"Order missing id field: {e}"}
    

    def create_order(self, order_data: dict) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                
                order_dict = order_data.model_dump()

                # Creating new order id based on last order added to order_data
                new_id = max([order['id'] for order in data], default=0) + 1
                order_dict['id'] = new_id
                order_dict["timestamp"] = datetime.now().isoformat()

                data.append(order_dict)
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return order_dict

        except FileNotFoundError:
            # create a new file and store the order data
            order_dict['id'] = 1
            with open(self.file_path, 'w') as f:
                json.dump([order_data], f, indent=4)
            return order_data
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}
        except KeyError as e:
            return {"error": f"Order missing id field: {e}"}
    
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
                    return {"error": f"Order with id {order_id} not found."}
                
                # Saving changes
                with open(self.file_path, 'w') as f:
                    json.dump(new_data, f, indent=4)

                return deleted_order
        except FileNotFoundError:
            return {"error": f"File {self.file_path} not found."}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}
        except KeyError as e:
            return {"error": f"Order missing id field: {e}"}
    
    def cancel_order(self, order_id: int) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            for i, order in enumerate(data):
                if order.get["id"] == order_id:

                    data[i] = {**order, **updates} # update the order with the new status
                    with open(self.file_path, 'w') as f:
                        json.dump(data, f, indent=4)
                    
                    return data[i]
                
                return{"error": f"Order with id {order_id} not found."}
            
        except FileNotFoundError:
            return {"error": f"File {self.file_path} not found."}
        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON: {e}"}
        
        
                    