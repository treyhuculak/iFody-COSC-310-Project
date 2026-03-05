from fastapi import HTTPException

from src.backend.models.order import Order, OrderCreate
from src.backend.models.order_item import OrderItem
from src.backend.repositories.order_repo import OrderRepository
from src.backend.models.order import OrderStatus


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
    
    def update_order_status(self, order_id: int, new_status: OrderStatus):
        updated_order = self.order_repo.update_order_status(order_id, new_status)
        if updated_order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        else:
            return updated_order


