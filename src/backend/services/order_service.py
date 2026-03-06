from typing import Optional

from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.models.order import OrderCreate
import json

'''
This service will handle all the business logic related to orders, such as calculating totals, taxes, and delivery fees. It will interact with the OrderRepository for data persistence and the RestaurantRepository for fetching restaurant-specific information like delivery fees.
'''

class OrderService:
    TAX_RATES = 'data/tax_rates.json'

    def __init__(self):
        self.restaurant_repo = RestaurantRepository()

    def calculate_order_subtotal(self, order: OrderCreate):
        total_price = 0
        for item in order.order_items:
            total_price += item.price * item.quantity     
        return total_price

    def calculate_tax(self, order: OrderCreate, order_subtotal: Optional[float] = None):
        try:
            with open(self.TAX_RATES, 'r') as f:
                tax_data = json.load(f)
                tax_rate = tax_data.get(order.location.value, 0)
                return (order_subtotal if order_subtotal is not None else self.calculate_order_subtotal(order)) * tax_rate
        except FileNotFoundError:
            raise ValueError("Tax rates file not found")
        except json.JSONDecodeError:
            raise ValueError("Error decoding tax rates file")


    def get_delivery_fee(self, order: OrderCreate):
        restaurant = self.restaurant_repo.get_restaurant_by_id(order.restaurant_id)
        if not restaurant:
            raise ValueError("Restaurant not found")
        return restaurant["delivery_fee"]
    
