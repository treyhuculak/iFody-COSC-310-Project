from fastapi import HTTPException

from src.backend.models.order import Order, OrderCreate
from src.backend.models.order_item import OrderItem, OrderItemCreate
from src.backend.repositories.order_repo import OrderRepository
from src.backend.models.order import OrderStatus
from src.backend.models.menu_item import MenuItem


class OrderController:
    def __init__(self) -> None:
        self.order_repo = OrderRepository()

    def get_order(self, order_id: int):
        order = self.order_repo.get_order_by_id(order_id)
        if order == None:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        return order

    def add_order(self, order: OrderCreate):      
        return self.order_repo.create_order(order)
        
    def delete_order(self, order_id: int):
        order = self.get_order(order_id)
        if (order["status"] == "pending" or order["status"] == "awaiting payment"):
            '''
            Ensure no punishment happens, since the order was canceled before the restaurant accepting it
            '''
            return self.order_repo.delete_order(order_id)
        elif(order["status"] == "payment confirmed" or order["status"] == "preparing"):
            '''
            Need some kind of punishment for cancelling after restaurant accepted the order
            '''
            return self.order_repo.delete_order(order_id)
        else:
            raise HTTPException(status_code=403, detail="Order already heading to you, it cannot be cancelled")
    
    def update_order_status(self, order_id: int, new_status: OrderStatus, role: str):
        if role != "manager":
            raise HTTPException(status_code=403, detail="Only managers can update order status")
        
        updated_order = self.order_repo.update_order_status(order_id, new_status)
        if updated_order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        else:
            return updated_order
        
    '''
    Order item operations for a specific order:
        - Add an order item to an order
        - Delete an order item from an order
    '''

    '''
    The idea here is that we pass the whole menu item and we create an order item from that menu item (basically so they have the same id - easier to recognize same items that way)
    Inside the repo we assign the item price/subtotal and the order id itself.
    '''
    def add_order_item_to_order(self, menu_item: MenuItem, order_id: int):
        order = self.get_order(order_id)
        # Checking if order should be able to be modified or not
        if not (order["status"] == "out for delivery" or order["status"] == "delivered"):

            # Creating order item based on menu item
            order_item = OrderItemCreate(item_id = menu_item.id, quantity = 1)
            if isinstance(order, dict) and "error" in order:
                raise HTTPException(status_code=404, detail=order["error"])
            
            # Note: Basic field validation (e.g., quantity > 0) is handled by the OrderItemCreate Pydantic model.
            order_item_data = order_item.model_dump()
            added_item = self.order_repo.add_order_item_to_order(order_item_data, order_id, menu_item.price)
            return added_item
        else:
            raise HTTPException(status_code=403, detail="Order already heading to you, it cannot be modified")
        
    def delete_order_item_from_order(self, order_id: int, order_item_id: int):
        order = self.get_order(order_id)

        # Checking if order should be able to be modified or not
        if not (order["status"] == "out for delivery" or order["status"] == "delivered"):
            deleted_item = self.order_repo.delete_order_item_from_order(order_id, order_item_id)
            return deleted_item 
        else:
            raise HTTPException(status_code=403, detail="Order already heading to you, it cannot be modified")
        
    def get_order_items_by_order_id(self, order_id: int):
        all_order_items = self.order_repo.get_order_items_from_order(order_id)
        return all_order_items
        


