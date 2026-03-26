from typing import Optional
from datetime import datetime
from fastapi import HTTPException

from src.backend.models.order import OrderCreate, OrderLocation, OrderStatus
from src.backend.models.order_item import OrderItemCreate
from src.backend.repositories.order_repo import OrderRepository
from src.backend.repositories.restaurant_repo import RestaurantRepository

from src.backend.services.order_service import OrderService
from src.backend.models.menu_item import MenuItem
from src.backend.models.review import Review, ReviewCreate
from src.backend.models.user import Role
from src.backend.controllers.notification_controller import NotificationController
from src.backend.models.notification import NotificationCreate, NotificationType
from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.models.delivery import DeliveryCreate
from src.backend.controllers.delivery_controller import DeliveryController

class OrderController:
    def __init__(self, repo: Optional[OrderRepository] = None, notif_controller: Optional[NotificationController] = None, delivery_controller: Optional[DeliveryController] = None) -> None:
        self.order_repo = repo or OrderRepository()
        self.notif_controller = notif_controller or NotificationController()
        self.delivery_controller = delivery_controller or DeliveryController()
        self.order_service = OrderService()
        self.restaurant_repo = RestaurantRepository()

    def _get_owner_id(self, restaurant_id: int) -> int:
        restaurant_info = self.restaurant_repo.get_restaurant_by_id(restaurant_id)
        owner_id = restaurant_info["owner_id"]
        return owner_id

    def add_order(self, order: OrderCreate):
        try:
            # Calculate totals first using the original order with Enum objects
            subtotal = self.order_service.calculate_order_subtotal(order)
            tax = self.order_service.calculate_tax(order, subtotal)
            delivery_fee = self.order_service.get_delivery_fee(order)
            
            # Now serialize the order data for storage
            order_data = order.model_dump()
            order_data['status'] = order.status.value
            order_data['location'] = order.location.value
            order_data['subtotal_price'] = subtotal
            order_data['tax'] = tax
            order_data['delivery_fee'] = delivery_fee
            order_data['total_price'] = subtotal + tax + delivery_fee

            new_order = self.order_repo.create_order(order_data)

            #Send manager and customer notifications regarding the new order
            customer_id = new_order["customer_id"]
            restaurant = self.restaurant_repo.get_restaurant_by_id(new_order["restaurant_id"])
            restaurant_name = restaurant["name"]
            order_id = new_order["id"]
            owner_id = self._get_owner_id(new_order["restaurant_id"])
            manager_notification = NotificationCreate(
                user_id= owner_id,
                type= NotificationType.NEW_ORDER_RECEIVED,
                title= "New Order Received",
                message= f"A new order with id {order_id} has been received.",
                is_read = False,
                order_id = order_id
            )
            self.notif_controller.create_notif(manager_notification)

            customer_notif = NotificationCreate(
                user_id = customer_id,
                type = NotificationType.NEW_ORDER_RECEIVED,
                title = "Order Confirmed",
                message = f"Your order at {restaurant_name} has been received, and is awaiting payment",
                is_read = False,
                order_id = new_order["id"]
            )
            self.notif_controller.create_notif(customer_notif)
            return new_order
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_order(self, order_id: int):
        order = self.order_repo.get_order_by_id(order_id)
        if order == None:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        return order
        
    def delete_order(self, order_id: int, user_id: int, user_role: Role):
        order = self.get_order(order_id)

        if(order["customer_id"] != user_id and user_role != Role.ADMIN):
            raise HTTPException(status_code=403, detail="You can only cancel your own orders")

        if (order["status"] == OrderStatus.PENDING.value or order["status"] == OrderStatus.AWAITING_PAYMENT.value or order["status"] == OrderStatus.PAYMENT_FAILED.value):
            owner_id = self._get_owner_id(order["restaurant_id"])
            manager_deleted_order_notif = NotificationCreate(
                user_id = owner_id,
                type = NotificationType.ORDER_CANCELLED,
                title = "Order Cancelled",
                message = f"Order with ID {order_id} has been cancelled by the customer before confirmation",
                is_read = False,
                order_id = order_id
            )
            self.notif_controller.create_notif(manager_deleted_order_notif)
            customer_del_order_notif = NotificationCreate(
                user_id = order["customer_id"],
                type = NotificationType.ORDER_CANCELLED,
                title = "Order Cancelled",
                message = f"Order {order_id} has been successfully cancelled before confirmation",
                is_read = False,
                order_id = order_id
            )  
            self.notif_controller.create_notif(customer_del_order_notif)
            return self.order_repo.delete_order(order_id)

        elif(order["status"] == OrderStatus.PAYMENT_CONFIRMED.value or order["status"] == OrderStatus.PREPARING_ORDER.value):
            owner_id = self._get_owner_id(order["restaurant_id"])
            manager_deleted_order_notif = NotificationCreate(
                user_id = owner_id,
                type = NotificationType.ORDER_CANCELLED,
                title = "Order Cancelled",
                message = f"Order with ID {order_id} has been cancelled by the customer after confirmation, fees will be applied",
                is_read = False,
                order_id = order_id
            )
            self.notif_controller.create_notif(manager_deleted_order_notif)
            customer_del_order_notif = NotificationCreate(
                user_id = order["customer_id"],
                type = NotificationType.ORDER_CANCELLED,
                title = "Order Cancelled",
                message = f"Order {order_id} has been cancelled after confirmation, fees will be applied",
                is_read = False,
                order_id = order_id
            )
            self.notif_controller.create_notif(customer_del_order_notif)
            return self.order_repo.delete_order(order_id)

        else:
            raise HTTPException(status_code=403, detail="Order already heading to you, it cannot be cancelled")
        
                    
    def update_order_status(self, order_id: int, new_status: str, role: str, transaction_is_successful: Optional[bool] = None):
        if role != "manager":
            raise HTTPException(status_code=403, detail="Only managers can update order status")
        
        # Getting order using order id
        order = self.get_order(order_id)

        # Updating status according to if transaction is accepted or not
        if(order['status'] == OrderStatus.AWAITING_PAYMENT.value):
            if(transaction_is_successful != None and transaction_is_successful):
                new_status = OrderStatus.PAYMENT_CONFIRMED
            else:
                new_status = OrderStatus.PAYMENT_FAILED
        # Since new_status is Out_for_delivery
        elif(order['status'] == OrderStatus.PREPARING_ORDER.value):
            delivery = DeliveryCreate(order_id=order_id)
            self.delivery_controller.create_delivery(delivery)
        # Since new_status is Delivered
        elif(order['status'] == OrderStatus.OUT_FOR_DELIVERY.value):
            delivery = self.delivery_controller.get_delivery_by_order_id(order_id)
            self.delivery_controller.assign_delivered_at_time(delivery["id"], datetime.now())
        
        # Convert string to OrderStatus enum
        try:
            status_enum = OrderStatus(new_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

        updated_order = self.order_repo.update_order_status(order_id, status_enum.value)
        if updated_order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        else:
            customer_status_map = {
                OrderStatus.PAYMENT_CONFIRMED: NotificationType.ORDER_CONFIRMED,
                OrderStatus.PAYMENT_FAILED: NotificationType.PAYMENT_FAILED,
                OrderStatus.PREPARING_ORDER: NotificationType.ORDER_IN_PROGRESS,
                OrderStatus.OUT_FOR_DELIVERY: NotificationType.ORDER_IN_TRANSIT,
                OrderStatus.DELIVERED: NotificationType.ORDER_DELIVERED
            }

            notif_type = customer_status_map.get(status_enum, NotificationType.ORDER_CONFIRMED)

            #create notification for the customer
            customer_notification = NotificationCreate(
                user_id = updated_order["customer_id"],
                type = notif_type,
                title = "Order Status Updated",
                message = f"Your order status is now {status_enum.value}",
                order_id=order_id,
                is_read=False
            )
            self.notif_controller.create_notif(customer_notification)

            manager_status_map = {
                OrderStatus.OUT_FOR_DELIVERY: (NotificationType.ORDER_IN_TRANSIT, "Driver Picked Up", f"Order #{order_id} picked up by driver"),
                OrderStatus.DELIVERED: (NotificationType.ORDER_DELIVERED, "Order has been delivered", f"Order #{order_id} has been delivered")
            }

            if status_enum in manager_status_map:
                notif_type, title, message = manager_status_map[status_enum]
                owner_id = self._get_owner_id(order["restaurant_id"])
                manager_notification = NotificationCreate(
                    user_id = owner_id,
                    type = notif_type,
                    title = title,
                    message = message,
                    order_id = order_id,
                    is_read = False
                )
                self.notif_controller.create_notif(manager_notification)
            
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
    def add_order_item_to_order(self, menu_item: MenuItem, order_id: int, quantity: int, user_id: int, user_role: Role):
        order = self.get_order(order_id)

        if (order["customer_id"] != user_id and user_role != Role.ADMIN):
            raise HTTPException(status_code=403, detail="You can only modify your own orders")
        if not (order["status"] == OrderStatus.OUT_FOR_DELIVERY.value or order["status"] == OrderStatus.DELIVERED.value):

            order_item = OrderItemCreate(item_id=menu_item.id, quantity=quantity)
            
            order_item_data = order_item.model_dump()
            added_item = self.order_repo.add_order_item_to_order(order_item_data, order_id, menu_item.price)
            item_name = menu_item.name
            owner_id = self._get_owner_id(order["restaurant_id"])
            added_item_manager_notif = NotificationCreate(
                user_id = owner_id,
                type = NotificationType.NEW_ITEM_ADDED,
                title = "New Item Added",
                message = f"Customer has added {item_name} to order #{order_id}",
                order_id = order_id,
                is_read = False
            )
            self.notif_controller.create_notif(added_item_manager_notif)

            # Re-fetch after mutation so totals are based on the latest order_items.
            updated_order = self.get_order(order_id)
            updated_subtotal = self.order_service.calculate_order_subtotal(OrderCreate(**updated_order))
            updated_tax = self.order_service.calculate_tax(OrderCreate(**updated_order), updated_subtotal)
            updated_delivery_fee = self.order_service.get_delivery_fee(OrderCreate(**updated_order))
            self.order_repo.update_order_pricing(order_id, updated_subtotal, updated_tax, updated_delivery_fee)
            
            return added_item
        else:
            raise HTTPException(status_code=403, detail="Order already heading to you, it cannot be modified")
        
    def delete_order_item_from_order(self, order_id: int, order_item_id: int, user_id: int, user_role: Role):
        order = self.get_order(order_id)

        # Check if user owns the order
        if(order["customer_id"] != user_id and user_role != Role.ADMIN):
            raise HTTPException(status_code=403, detail="You can only modify your own orders")
        
        # Checking if order should be able to be modified or not
        if not (order["status"] == OrderStatus.OUT_FOR_DELIVERY.value or order["status"] == OrderStatus.DELIVERED.value):
            deleted_item = self.order_repo.delete_order_item_from_order(order_id, order_item_id)
            return deleted_item 
        else:
            raise HTTPException(status_code=403, detail="Order already heading to you, it cannot be modified")
        
    def get_order_items_by_order_id(self, order_id: int):
        all_order_items = self.order_repo.get_order_items_from_order(order_id)
        return all_order_items
    
    # Review functionality

    def get_review_by_order_id(self, order_id: int):
        '''
        Get the review for a specific order. Raises an HTTPException if not found.
        '''
        review = self.order_repo.get_review_by_order_id(order_id)
        if review is None:
            raise HTTPException(status_code=404, detail="Review not found for this order")
        return review
    
    def add_review_to_order(self, order_id: int, review: ReviewCreate) -> Review:
        '''
        Add a review to a specific order. Raises an HTTPException if the order already has a review.
        '''
        review_data = review.model_dump()
        added_review = self.order_repo.add_review_to_order(order_id, review_data)
        return Review(**added_review)
    
    def delete_review_from_order(self, order_id: int) -> Review:
        '''
        Delete the review from a specific order. Raises an HTTPException if no review exists for the order.
        '''
        deleted_review = self.order_repo.delete_review_from_order(order_id)
        return Review(**deleted_review)
    
    def update_review_from_order(self, order_id: int, review: ReviewCreate) -> Review:
        '''
        Update the review for a specific order. Adds the review if a previous order doesn't exist.
        '''
        review_data = review.model_dump()
        updated_review = self.order_repo.update_review_from_order(order_id, review_data)
        return Review(**updated_review)
