from typing import Optional
from fastapi import HTTPException

from src.backend.models.delivery import DeliveryCreate
from src.backend.repositories.delivery_repo import DeliveryRepository
from src.backend.repositories.order_repo import OrderRepository
from src.backend.services.delivery_service import DeliveryService

class DeliveryController:
    def __init__(self, repo: Optional[DeliveryRepository] = None, order_repo: Optional[OrderRepository] = None) -> None:
        self.delivery_repo = repo or DeliveryRepository()
        self.order_repo = order_repo or OrderRepository()
        self.delivery_service = DeliveryService()

    def create_delivery(self, delivery: DeliveryCreate):
        try:
            # Now serialize the delivery data for storage
            delivery_data = delivery.model_dump()
            order = self.order_repo.get_order_by_id(delivery_data["order_id"])
            delivery_data["estimated_delivery_time"] = self.delivery_service.calculate_estimated_delivery_time(order["location"])
            flag = self.delivery_service.assign_delivery_driver(delivery_data)

            if not flag:
                raise HTTPException(status_code=400, detail="No delivery driver was found around your area")

            new_delivery = self.delivery_repo.create_delivery(delivery_data)
            
            return new_delivery
        except HTTPException as e:
            raise
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def get_delivery(self, delivery_id: int):
        delivery = self.delivery_repo.get_delivery_by_id(delivery_id)
        if delivery == None:
            raise HTTPException(status_code=404, detail=f"Delivery {delivery_id} not found")
        return delivery
    
    def get_delivery_by_order_id(self, order_id: int):
        delivery = self.delivery_repo.get_delivery_by_order_id(order_id)
        if delivery == None:
            raise HTTPException(status_code=404, detail=f"Delivery not found")
        return delivery
    
    def delete_delivery(self, delivery_id: int):
        return self.delivery_repo.delete_delivery(delivery_id)
    
    def assign_delivered_at_time(self, delivery_id: int, time: str):
        self.delivery_repo.assign_delivered_at_time(delivery_id, time)
    
