from typing import Optional
from src.backend.models.order import Order, OrderCreate
from src.backend.repositories.order_repo import OrderRepository
from src.backend.services.order_service import OrderService
from fastapi import HTTPException

class OrderController:
    def __init__(self, repo: Optional[OrderRepository] = None) -> None:
        self.repo = repo or OrderRepository()
        self.service = OrderService()

    def create_order(self, order_data):
        pass

    def get_order(self, order_id):
        pass

    def update_order_status(self, order_id, new_status):
        pass

    def calculate_order_total(self, order: Order):
        try:
            total = self.service.calculate_order_total(order)
            return total
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="An unexpected error occurred while calculating the order total.")


    # Build Reciept -> calc_item_total -> calc_tax -> get_delivery_fee -> calc_grand_total