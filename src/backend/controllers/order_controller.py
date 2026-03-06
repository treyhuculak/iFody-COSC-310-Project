from typing import Optional

from fastapi import HTTPException

from src.backend.models.order import Order, OrderCreate
from src.backend.models.order_item import OrderItem
from src.backend.repositories.order_repo import OrderRepository
from src.backend.services.order_service import OrderService


class OrderController:
    def __init__(self, repo: Optional[OrderRepository] = None) -> None:
        self.order_repo = repo or OrderRepository()
        self.order_service = OrderService()
    
    def validate_order_logic(self):
        # For now
        return True

    def add_order(self, order: OrderCreate):
        try:
            order_data = order.model_dump(mode="json")

            # Calculate total price, tax, and delivery fee before saving the order
            order_data['subtotal_price'] = self.order_service.calculate_order_subtotal(order)
            order_data['tax'] = self.order_service.calculate_tax(order, order_data['subtotal_price'])
            order_data['delivery_fee'] = self.order_service.get_delivery_fee(order)
            order_data['total_price'] = order_data['subtotal_price'] + order_data['tax'] + order_data['delivery_fee']

            return self.order_repo.create_order(order_data)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the order.")
        
    def delete_order(self, order_id: int):
        return self.order_repo.delete_order(order_id)
    
    def get_order(self, order_id: int):
        order = self.order_repo.get_order_by_id(order_id)
        if order == None:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        return order
