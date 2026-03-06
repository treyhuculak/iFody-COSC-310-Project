from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from src.backend.controllers.order_controller import OrderController
from src.backend.models.order import Order, OrderCreate
from src.backend.models.order_item import OrderItem

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

def get_controller():
    return OrderController()

@router.post("/", response_model=Order)
def add_order(order: OrderCreate, controller: OrderController = Depends(get_controller)):
    new_order = controller.add_order(order)
    return new_order

@router.delete("/{order_id}", response_model=Order)
def delete_order(order_id: int, controller: OrderController = Depends(get_controller)):
    deleted_order = controller.delete_order(order_id)
    return deleted_order

@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int, controller: OrderController = Depends(get_controller)):
    return controller.get_order(order_id)

@router.put("/{order_id}/status", response_model=Order)
def update_order_status(order_id: int, new_status: str, role: str, controller: OrderController = Depends(get_controller)):
    return controller.update_order_status(order_id, new_status, role)
'''
@router.delete("/{order_id}/order/{order_item_id}", response_model=OrderItem)
def delete_order_item(order_id: int, order_item_id: int, controller: OrderController = Depends(get_controller)):
    deleted_item = controller.delete_order_item(order_id, order_item_id)
    return deleted_item
'''