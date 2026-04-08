import json
from src.backend.models.order import OrderCreate
from src.backend.models.offer import OfferType
from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.services.offer_service import OfferService
from typing import Optional

class OrderService:
    '''
    This service will handle all the business logic related to orders, such as calculating totals, taxes, and delivery fees. It will interact with the OrderRepository for data persistence and the RestaurantRepository for fetching restaurant-specific information like delivery fees.
    '''
    TAX_RATES = 'data/tax_rates.json'

    def __init__(self):
        self.restaurant_repo = RestaurantRepository()
        self.offer_service = OfferService()

    def calculate_order_subtotal(self, order: OrderCreate):
        total_price = 0
        active_offer = self.offer_service.get_active_offer()

        for item in order.order_items:
            total_price += item.price_at_purchase * item.quantity
        
        if active_offer:
            if active_offer["offer_type"] == OfferType.DISCOUNT.value:
                if active_offer["restaurant_id"] == order.restaurant_id:
                    total_price *= (1 - (active_offer["discount_value"] / 100))
            elif active_offer["offer_type"] == OfferType.FREE_ITEM.value:
                if active_offer["restaurant_id"] == order.restaurant_id:
                    for free_item_id in active_offer["applied_items"]:
                        for item in order.order_items:
                            if item.item_id == free_item_id:
                                if total_price - item.price_at_purchase > 0:
                                    total_price -= item.price_at_purchase
                                    break
            else:
                if active_offer["restaurant_id"] == order.restaurant_id:
                    for applied_item_id in active_offer["applied_items"]:
                        for item in order.order_items:
                            if item.item_id == applied_item_id:
                                total_price -= (item.price_at_purchase - active_offer["price_ceiling"])
                                break

        return total_price

    def calculate_tax(self, order: OrderCreate, order_subtotal: Optional[float] = None):
        try:
            with open(self.TAX_RATES, 'r') as f:
                tax_data = json.load(f)
                tax_rate = tax_data.get(order.location.value, 0)
                return order_subtotal * tax_rate
        except FileNotFoundError:
            raise ValueError("Tax rates file not found")
        except json.JSONDecodeError:
            raise ValueError("Error decoding tax rates file")

    def get_delivery_fee(self, order: OrderCreate):
        restaurant = self.restaurant_repo.get_restaurant_by_id(order.restaurant_id)
        if not restaurant:
            raise ValueError("Restaurant not found")
        return restaurant["delivery_fee"]