from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from src.backend.controllers.order_controller import OrderController
from src.backend.models.order import Order, OrderCreate
from src.backend.models.order_item import OrderItem, OrderItemCreate
from src.backend.models.menu_item import MenuItem

router = APIRouter(
    prefix="/order",
    tags=["order"]
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

@router.delete("/{order_id}/items/{item_id}", response_model=OrderItem)
def delete_order_item(order_id: int, item_id: int, controller: OrderController = Depends(get_controller)):
    deleted_item = controller.delete_order_item_from_order(order_id, item_id)
    return deleted_item

@router.post("/{order_id}/items", response_model=OrderItem)
def add_order_item(order_id: int, order_item: MenuItem, controller: OrderController = Depends(get_controller)):
    new_item = controller.add_order_item_to_order(order_item, order_id)
    return new_item

@router.get("/{order_id}/items", response_model=List[OrderItem])
def get_all_order_items(order_id: int, controller: OrderController = Depends(get_controller)):
    return controller.get_order_items_by_order_id(order_id)

@router.get("/{order_id}/items/{item_id}", response_model=OrderItem)
def get_order_item_by_id(order_id: int, item_id: int, controller: OrderController = Depends(get_controller)):
    order_items = controller.get_order_items_by_order_id(order_id)
    if isinstance(order_items, list):
        for item in order_items:
            if isinstance(item, dict) and item.get("item_id") == item_id:
                return item
    raise HTTPException(status_code=404, detail="Order item not found")
