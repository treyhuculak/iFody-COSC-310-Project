# import json
# import os
# from unittest.mock import patch
# import pytest
# from fastapi.testclient import TestClient
# from src.backend.main import app
# from src.backend.models.order import OrderCreate, OrderStatus, OrderLocation
# from src.backend.routers.orders import get_controller
# from src.backend.models.order_item import OrderItem
# from src.backend.repositories.order_repo import OrderRepository
# from src.backend.controllers.order_controller import OrderController
# from src.backend.services.order_service import OrderService
# from src.backend.models.offer import OfferType
# from src.backend.repositories.notification_repo import NotificationRepository
# from src.backend.controllers.notification_controller import NotificationController
# from src.backend.repositories.user_repo import UserRepository
# import src.backend.utils.auth_dependencies as auth_dependencies

# @pytest.fixture
# def test_client(tmp_path):
#     """
#     Provides a TestClient backed by a temporary JSON file instead of the real
#     data/orders.json.  The temp file is deleted automatically after each
#     test, so the production database is never touched.
#     """
#     temp_db = tmp_path / "test_orders.json"
#     temp_db.write_text(json.dumps([]))

#     temp_notif_db = tmp_path / "test_notifications.json"
#     temp_notif_db.write_text(json.dumps([]))

#     temp_user_db = tmp_path / "test_users.json"
#     temp_user_db.write_text(json.dumps({
#         "Users": [
#             {
#                 "id": 1,
#                 "username": "TestCustomer",
#                 "email": "testcustomer@example.com",
#                 "password": "Test@123",
#                 "role": "customer",
#                 "is_logged_in": False,
#                 "is_blocked": False
#             },
#             {
#                 "id": 2,
#                 "username": "TestOwner",
#                 "email": "testowner@example.com",
#                 "password": "Test@123",
#                 "role": "owner",
#                 "is_logged_in": False,
#                 "is_blocked": False
#             } 
#         ]}))

#     test_repo = OrderRepository(file_path=str(temp_db))
#     test_notif_repo = NotificationRepository(file_path=str(temp_notif_db))
#     test_user_repo = UserRepository(file=str(temp_user_db))

#     test_notif_controller = NotificationController(repo=test_notif_repo)
#     test_controller = OrderController(repo=test_repo, notif_controller=test_notif_controller)

#     app.dependency_overrides[get_controller] = lambda: test_controller

#     original_repo = auth_dependencies.repo
#     auth_dependencies.repo = test_user_repo

#     with TestClient(app) as client:
#         client.headers.update({"X-User-Id": "1"})  
#         yield client

#     auth_dependencies.repo = original_repo
#     app.dependency_overrides.clear()

# order_items = [
#     OrderItem(item_id=1, price_at_purchase=10.0, quantity=2),
#     OrderItem(item_id=2, price_at_purchase=5.0, quantity=1)
# ]

# order = OrderCreate(customer_id=1, restaurant_id=1, location=OrderLocation.BRITISH_COLUMBIA, order_items=order_items, status=OrderStatus.PENDING)

# # Unit tests for OrderService
# def test_calculate_order_subtotal():
#     order_service = OrderService("data/temp_offers.json")
    
#     total = order_service.calculate_order_subtotal(order)
#     assert total == 25.0
#     os.remove(os.getcwd() + "/data/temp_offers.json")


# def test_calculate_order_subtotal_with_discount():
#     order_service = OrderService("data/temp_offers.json")
#     # Apply a 10% discount for the restaurant
#     with patch('src.backend.services.order_service.OfferService.get_active_offer', return_value={
#         "offer_type": OfferType.DISCOUNT.value,
#         "restaurant_id": 1,
#         "discount_value": 10
#     }):
#         total = order_service.calculate_order_subtotal(order)
#         assert total == 22.5
#     os.remove(os.getcwd() + "/data/temp_offers.json")


# def test_calculate_order_subtotal_with_free_item():
#     order_service = OrderService("data/temp_offers.json")
#     # Make item with id 1 free
#     with patch('src.backend.services.order_service.OfferService.get_active_offer', return_value={
#         "offer_type": OfferType.FREE_ITEM.value,
#         "restaurant_id": 1,
#         "applied_items": [1]
#     }):
#         total = order_service.calculate_order_subtotal(order)
#         # Original total 25.0 minus item 1 price 10.0 -> 15.0
#         assert total == 15.0
#         os.remove(os.getcwd() + "/data/temp_offers.json")


# def test_calculate_order_subtotal_with_price_ceiling():
#     order_service = OrderService("data/temp_offers.json")
#     # Apply a price ceiling of 8.0 for item 1 (reduces price by 2.0)
#     with patch('src.backend.services.order_service.OfferService.get_active_offer', return_value={
#         "offer_type": OfferType.PRICE_CEILING.value,
#         "restaurant_id": 1,
#         "applied_items": [1],
#         "price_ceiling": 8.0
#     }):
#         total = order_service.calculate_order_subtotal(order)
#         # 25.0 - (10.0 - 8.0) == 23.0
#         assert total == 23.0
#         os.remove(os.getcwd() + "/data/temp_offers.json")

# def test_calculate_tax():
#     order_service = OrderService("data/temp_offers.json")
    
#     subtotal = order_service.calculate_order_subtotal(order)
#     assert subtotal == 25.0

#     tax = order_service.calculate_tax(order, subtotal)
#     assert tax == 3.0  # Assuming a tax rate of 12% for British Columbia
#     os.remove(os.getcwd() + "/data/temp_offers.json")


# # Integration test for OrderController
# def test_add_order(test_client):
#     # Mock the get_delivery_fee method to return a fixed delivery fee for testing
#     with patch('src.backend.services.order_service.OrderService.get_delivery_fee', return_value=5):
#         response = test_client.post("/orders/", json=order.model_dump(mode="json"))
#         assert response.status_code == 200

#         data = response.json()
#         assert data["customer_id"] == order.customer_id
#         assert data["restaurant_id"] == order.restaurant_id
#         assert data["location"] == order.location.value
#         assert len(data["order_items"]) == len(order.order_items)
#         assert data["subtotal_price"] == 25.0
#         assert data["tax"] == 3.0
#         assert data["delivery_fee"] == 5.0
#         assert data["total_price"] == 25.0 + 3.0 + 5.0

# def test_get_delivery_fee():
#     order_service = OrderService("data/temp_offers.json")
#     # Mock the restaurant repository to return a specific delivery fee
#     with patch.object(order_service.restaurant_repo, 'get_restaurant_by_id', return_value={"delivery_fee": 7.5}):
#         fee = order_service.get_delivery_fee(order)
#         assert fee == 7.5
#     os.remove(os.getcwd() + "/data/temp_offers.json")

# def test_subtotal_and_tax_updates(test_client):
#     # This is to test the bug fix where subtotal and tax were not updating after adding an item to an existing order. This test will create an order with items, then later add another item to it, and then check if the subtotal and tax are updated correctly.
    
#     with patch('src.backend.services.order_service.OrderService.get_delivery_fee', return_value=5):
#         # Create the initial order
#         response = test_client.post("/orders/", json=order.model_dump(mode="json"))
#         assert response.status_code == 200
#         data = response.json()
#         order_id = data["id"]

#         prev_subtotal = data["subtotal_price"]
#         prev_tax = data["tax"]

#         # Add another item to the existing order
#         menu_item = {
#             "name": "Test Menu Item",
#             "description": "A menu item for testing",
#             "price": 8.00,
#             "id": 0
#         }
#         add_response = test_client.post(f"/orders/{order_id}/items", params={"quantity": 1}, json=menu_item)
#         assert add_response.status_code == 200

#         # Get the updated order details
#         get_order_response = test_client.get(f"/orders/{order_id}")
#         assert get_order_response.status_code == 200
#         updated_order = get_order_response.json()

#         new_subtotal = updated_order["subtotal_price"]
#         new_tax = updated_order["tax"]

#         # Check if the subtotal and tax are updated correctly
#         expected_subtotal = prev_subtotal + (8.0)  # Original subtotal + new item price
#         expected_tax = expected_subtotal * 0.12  # Assuming a tax rate of 12%
        
#         assert updated_order["subtotal_price"] == expected_subtotal
#         assert updated_order["tax"] == expected_tax
#         assert new_subtotal != prev_subtotal
#         assert new_tax != prev_tax