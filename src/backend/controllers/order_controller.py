from fastapi import HTTPException

from src.backend.models.order import Order, OrderCreate
from src.backend.models.order_item import OrderItem
from src.backend.repositories.order_repo import OrderRepository


class OrderController:
    def __init__(self) -> None:
        self.order_repo = OrderRepository()

    def add_order(self, order: OrderCreate):      
        return self.order_repo.create_order(order)
        
    def delete_order(self, order_id: int):
        return self.order_repo.delete_order(order_id)
    
    def get_order(self, order_id: int):
        order = self.order_repo.get_order_by_id(order_id)
        if order == None:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        return order
    
    def calculate_order_total(self):
        pass

    def update_order_status(self, new_status: str):
        pass

