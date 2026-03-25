from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from src.backend.controllers.delivery_controller import DeliveryController
from src.backend.models.delivery import DeliveryCreate, Delivery

router = APIRouter(
    prefix="/deliveries",
    tags=["deliveries"]
)

def get_controller():
    return DeliveryController()

@router.post("/", response_model=Delivery)
def add_delivery(delivery: DeliveryCreate, controller: DeliveryController = Depends(get_controller)):
    new_delivery = controller.create_delivery(delivery)
    return new_delivery

@router.get("/{delivery_id}", response_model=Delivery)
def get_delivery(delivery_id: int, controller: DeliveryController = Depends(get_controller)):
    return controller.get_delivery(delivery_id)

@router.delete("/{delivery_id}", response_model=Delivery)
def delete_delivery(delivery_id: int, controller: DeliveryController = Depends(get_controller)):
    deleted_delivery = controller.delete_delivery(delivery_id)
    return deleted_delivery

@router.put("/{delivery_id}/{time}")
def update_delivery(delivery_id: int, time: str, controller: DeliveryController = Depends(get_controller)):
    controller.assign_delivered_at_time(delivery_id, time)
    return {"message": f"Delivery {delivery_id} was delivered at: {time}"}

@router.get("/order_id/{order_id}", response_model=Delivery)
def get_delivery_by_order_id(order_id: int, controller: DeliveryController = Depends(get_controller)):
    return controller.get_delivery_by_order_id(order_id)