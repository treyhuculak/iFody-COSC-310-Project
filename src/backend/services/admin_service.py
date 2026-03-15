from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.repositories.order_repo import OrderRepository

class AdminService:
    def __init__(
            self,
            rest_repo_file: str = None,
            order_repo_file: str = None
        ):
        '''
        Initializes the AdminService class's attributes.
        '''
        self.rest_repo = RestaurantRepository(rest_repo_file)
        self.order_repo = OrderRepository(order_repo_file)

    def get_all_orders(self) -> list[dict]:
        '''
        Gets all the orders from all the restaurant instances.
        '''
        restaurants = self.rest_repo.get_all_restaurants()[0]
        orders = []
        for restaurant in restaurants:
            restaurant_id = restaurant["id"]
            order = self.order_repo.get_order_by_id(restaurant_id)
            orders.append(order)
        return orders
    
    def get_most_popular_restaurant(self) -> dict | None:
        '''
        Retrieves the restaurant instance with the highest number of orders.
        '''
        rests_and_orders = dict()
        for order in self.get_all_orders():
            if order["restaurant_id"] in rests_and_orders:
                order["restaurant_id"] += 1
            else:
                order["restaurant_id"] = 1
        if not rests_and_orders:
            return None
        most_popular_restaurant = max(rests_and_orders, key = rests_and_orders.get)
        return most_popular_restaurant