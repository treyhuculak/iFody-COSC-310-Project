from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.repositories.order_repo import OrderRepository
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

    def get_all_orders(self) -> list[dict]:
        '''
        Gets all the orders from all the restaurant instances.
        '''
        restaurants = self.rest_repo.get_all_restaurants()[0]
        orders = []
        for restaurant in restaurants:
            restaurant_id = restaurant["id"]
            order = self.order_repo.get_order_by_id(restaurant_id)
            if order:
                orders.append(order)
        return orders
    
    def get_most_popular_restaurant(self) -> Union[dict, None]:
        '''
        Retrieves the restaurant instance with the highest number of orders.
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