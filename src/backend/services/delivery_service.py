from datetime import datetime, timedelta
from src.backend.models.order import OrderLocation

'''
This service will handle all the business logic related to deliveries, such as assigning delivery driver. It will interact with the DeliveryController for data consistency.
'''

class DeliveryService:

    def __init__(self):
        pass

    def assign_delivery_driver(self, delivery_data: dict) -> bool:
        flag = True
        estimated_delivery_time_str = delivery_data["estimated_delivery_time"]
        edt = datetime.fromisoformat(estimated_delivery_time_str)
        if(edt > datetime.now() + timedelta(minutes = 60)):
            flag = False
        else:
            delivery_data["driver_id"] = 1 # TBD
            delivery_data["assigned_at"] = datetime.now().isoformat() 
        
        return flag
    
    def calculate_estimated_delivery_time(self, location: OrderLocation) -> datetime:
        dt = 0
        if(location == OrderLocation.BRITISH_COLUMBIA.value):
            dt = 30
        else:
            dt = 120
        
        return (datetime.now() + timedelta(minutes = dt)).isoformat()
