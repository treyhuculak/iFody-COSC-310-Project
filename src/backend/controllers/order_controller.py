from fastapi import HTTPException

from src.backend.models.order import Order, OrderCreate
from src.backend.models.order_item import OrderItem
from src.backend.repositories.order_repo import OrderRepository


class OrderController:
    def __init__(self) -> None:
        self.order_repo = OrderRepository()

    def validate_order_logic(self):
        # For now
        return True

    def add_order(self, order: OrderCreate):
        flag = self.validate_order_logic()
        if flag:
            return self.order_repo.create_order(order)
        else:
            raise HTTPException(status_code=404, detail="Order Logic is not correct")
        
    def delete_order(self, order_id: int):
        return self.order_repo.delete_order(order_id)
    
    def get_order(self, order_id: int):
        order = self.order_repo.get_order_by_id(order_id)
        if order == None:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        return order

    def cancel_order(self, order_id: int):
        order = self.order_repo.get_order_by_id(order_id) # Get order from repo
        if order == None:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        
        status = str(order.get("status", " ")).strip().lower() # Make Status into a uniformed format to compare

        # If the status are in these status, then the order can't be cancelled
        locked_statuses = ["payment confirmed", "preparing", "out for delivery", "delivered"]
        
        if status in locked_statuses:
            raise HTTPException(status_code=403, detail=f"Order is already being prepared and cannot be cancelled")
        if status in ["cancelled"]:
            return order
        
        # update the order to cancelled
        updated = self.order_repo.update_order_status(order_id, {"status": "cancelled"})

        # If the update return error, then make it HTTPException
        if isinstance(updated, dict) and "error" in updated:
            raise HTTPException(status_code=404, detail=f"error")
        
        # return updated order
        return updated