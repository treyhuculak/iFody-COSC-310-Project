import json
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException

class DeliveryRepository:
    DELIVERY_FILE = 'data/delivery.json'

    def __init__(self, file_path: Optional[str] = None) -> None:
        # check if files exist, if not create them with headers
        self.file_path = file_path or self.DELIVERY_FILE
        try:
            with open(self.file_path, 'r') as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # file doesn't exist or is corrupted, create/reset it with an empty list
            with open(self.file_path, 'w') as f:
                json.dump([], f, indent=4)
        pass

    def create_delivery(self, delivery_data: dict) -> dict:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)

                # Creating new delivery id based on last delivery added to delivery_data
                new_id = max([delivery['id'] for delivery in data], default=0) + 1
                delivery_data['id'] = new_id
                
                data.append(delivery_data)
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return delivery_data

        except FileNotFoundError:
            # create a new file and store the delivery data
            delivery_data['id'] = 1
            with open(self.file_path, 'w') as f:
                json.dump([delivery_data], f, indent=4)
            return delivery_data
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Delivery missing id field: {e}")
        
    def get_delivery_by_id(self, delivery_id: int) -> Optional[dict]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                # Getting the first delivery that matches the provided delivery_id 
                delivery = next(filter(lambda d: d.get("id") == delivery_id, data), None)
                return delivery
                    
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Delivery missing id field: {e}")
        
    def get_delivery_by_order_id(self, order_id: int) -> Optional[dict]:
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                # Getting the first delivery that matches the provided order_id 
                delivery = next(filter(lambda d: d.get("order_id") == order_id, data), None)
                return delivery
                    
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Delivery missing order_id field: {e}")
        
    def delete_delivery(self, delivery_id: int) -> dict:
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    new_data = data.copy()
                    deleted_delivery = None
                    
                    # Iterating data to find the delivery key and then deleting it from new_data
                    for k, d in enumerate(data):
                        if d["id"] == delivery_id:
                            deleted_delivery = new_data.pop(k)
                            break
                    
                    # If nothing is found
                    if deleted_delivery == None:
                        raise HTTPException(status_code=404, detail=f"Delivery with id {delivery_id} not found.")
                    
                    # Saving changes
                    with open(self.file_path, 'w') as f:
                        json.dump(new_data, f, indent=4)

                    return deleted_delivery
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
            except KeyError as e:
                raise HTTPException(status_code=500, detail=f"Delivery missing id field: {e}")
            
    def assign_delivered_at_time(self, delivery_id: int, time: str):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                # Updating the delivery delivered_at parameter
                new_data = []
                for delivery in data:
                    if(delivery["id"] == delivery_id):
                        delivery["delivered_at"] = time

                    new_data.append(delivery)

                # Saving changes
                with open(self.file_path, 'w') as f:
                    json.dump(new_data, f, indent=4)
                    
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {self.file_path} not found.")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {e}")
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Delivery missing user id field: {e}")