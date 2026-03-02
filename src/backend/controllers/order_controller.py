from fastapi import HTTPException
from datetime import datetime

from src.backend.models.order import Order
from src.backend.models.order_item import OrderItem
from src.backend.repositories.order_repo import OrderRepository


class OrderController:
    def __init__(self) -> None:
        self.order_repo = OrderRepository()

    def validate_order_logic():
        # For now
        return True

    def create_order(self, order: Order):
        flag = self.validate_order_logic()
        if flag:
            return self.order_repo.create_order(order)
        else:
            raise HTTPException(status_code=404, detail="Order Logic is not correct")
        
    def cancel_order(order_id: int):
        return self.order_repo.delete_order(order_id)
    

