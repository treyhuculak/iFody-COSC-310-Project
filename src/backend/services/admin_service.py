from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.repositories.order_repo import OrderRepository
from src.backend.services.order_service import OrderService
from typing import Union

class AdminService:
    def __init__(
            self,
            draft_order_db: str = None
        ):
        '''
        Initializes the AdminService class's attributes.
        '''
        self.rest_repo = RestaurantRepository()
        self.order_repo = OrderRepository(draft_order_db) if draft_order_db else OrderRepository()
        self.order_service = OrderService()

    def get_all_orders(self) -> list[dict]:
        '''
        Gets all the orders from all the restaurant instances.
        '''
        return self.order_repo.get_all_orders_for_admin()
    
    def get_gross_revenue_by_restaurant_id(self, restaurant_id: int) -> float:
        '''
        Returns the total revenue of the restaurant before deducting costs, based on the restaurant id.
        '''
        orders = self.get_all_orders()
        gross_revenue = 0
        matched_orders = [order for order in orders if order["restaurant_id"] == restaurant_id]
        for order in matched_orders:
            total_price_before_tax = self.order_service.calculate_order_subtotal(order)
            tax_required = self.order_service.calculate_tax(order, total_price_before_tax)
            gross_revenue += total_price_before_tax + tax_required
        return gross_revenue
    
    def get_average_delivery_time(self) -> float:
        '''
        Calculates the average delivery time of all the orders.
        Since the order instances do not include any time-related attribute, we will generate a random average delivery time between 10 and 60 minutes.
        '''
        import random
        upper_delivery_time_bound = 60
        lower_delivery_time_bound = 10
        average_delivery_time = random.uniform(lower_delivery_time_bound, upper_delivery_time_bound)
        return average_delivery_time
    
    def get_most_popular_restaurant(self) -> Union[dict, None]:
        '''
        Retrieves the restaurant instance with the highest number of orders.
        If some restaurants have the same number of orders, the restaurant with the lowest id is returned.
        '''
        rests_and_orders = dict()
        orders = self.get_all_orders()
        if not orders:
            return None
        for order in orders:
            restaurant_id = order["restaurant_id"]
            if restaurant_id in rests_and_orders:
                rests_and_orders[restaurant_id] += 1
            else:
                rests_and_orders[restaurant_id] = 1
        if not rests_and_orders:
            return None
        most_popular_restaurant_id = max(rests_and_orders, key = rests_and_orders.get)
        most_popular_restaurant = self.rest_repo.get_restaurant_by_id(most_popular_restaurant_id)
        return most_popular_restaurant