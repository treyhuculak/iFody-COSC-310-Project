# import pytest
# import json
# from fastapi.testclient import TestClient
# from src.backend.models.order import OrderStatus, OrderLocation
# from src.backend.models.notification import NotificationType
# from src.backend.models.user import Role
# from src.backend.controllers.order_controller import OrderController
# from src.backend.controllers.notification_controller import NotificationController
# from src.backend.repositories.order_repo import OrderRepository
# from src.backend.repositories.notification_repo import NotificationRepository
# from src.backend.repositories.user_repo import UserRepository
# from src.backend.repositories.restaurant_repo import RestaurantRepository
# import src.backend.utils.auth_dependencies as auth_dependencies
# from src.backend.routers.orders import get_controller
# from src.backend.main import app

# @pytest.fixture
# def test_client(tmp_path):

#     temp_db = tmp_path / "test.json"
#     temp_notif_db = tmp_path / "test_notif.json"
#     temp_restaurant_db = tmp_path / "test.restaurant.json"
#     temp_user_db = tmp_path / "test_users.json"

#     temp_db.write_text(json.dumps([]))
#     temp_notif_db.write_text(json.dumps([]))
#     temp_restaurant_db.write_text(json.dumps([]))

#     temp_user_db.write_text(json.dumps({
#         "Users": [
#             {
#                 "id": 1,
#                 "username": "TestCustomer",
#                 "email": "testcustomer@123.com",
#                 "password": "Test@123",
#                 "role": Role.CUSTOMER.value, 
#                 "is_logged_in": False,
#                 "is_blocked": False
#             },
#             {
#                 "id": 2,
#                 "username": "TestOwner",
#                 "email": "testowner@123.com",
#                 "password": "Test@123",
#                 "role": Role.RESTAURANT_OWNER.value,
#                 "is_logged_in": False,
#                 "is_blocked": False
#             },
#             {
#                 "id": 3,
#                 "username": "TestAdmin",
#                 "email": "testadmin@123.com",
#                 "password": "Test@123",
#                 "role": Role.ADMIN.value,
#                 "is_logged_in": False,
#                 "is_blocked": False
#             }
#         ]
#     }))
#     temp_restaurant_db.write_text(json.dumps([{
#         "id": 1,
#         "name": "Fake Rest",
#         "cuisine": "italian",
#         "location": "british columbia",
#         "delivery_fee": 2.99,
#         "owner_id": 2,
#         "is_available": True
#     }]))
#     test_user_repo = UserRepository(file=str(temp_user_db))

#     test_repo = OrderRepository(file_path=str(temp_db))
#     test_notif_repo = NotificationRepository(file_path=str(temp_notif_db))
#     test_restaurant_repo = RestaurantRepository(file_path=str(temp_restaurant_db))

#     test_notif_controller = NotificationController(repo=test_notif_repo)

#     test_controller = OrderController(
#         repo=test_repo, 
#         notif_controller=test_notif_controller
#     )
#     test_controller.restaurant_repo = test_restaurant_repo

    

#     app.dependency_overrides[get_controller] = lambda: test_controller
#     original_repo = auth_dependencies.repo
#     auth_dependencies.repo = test_user_repo

#     client = TestClient(app)
#     client.headers.update({"X-User-Id": "1"})

#     yield client, temp_notif_db


#     auth_dependencies.repo = original_repo
#     app.dependency_overrides.clear()


# def test_add_order_notifications(test_client):
#     client, temp_notif_db = test_client
#     new_order = {
#         "customer_id": 1,
#         "restaurant_id": 1,
#         "status": OrderStatus.PENDING.value,
#         "location": OrderLocation.BRITISH_COLUMBIA.value,
#         "order_items": [
#             {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
#         ]
#     }
#     response = client.post("/orders/", json=new_order)
#     assert response.status_code == 200
#     notifications = json.loads(temp_notif_db.read_text())
#     assert len(notifications) == 2
#     assert notifications[0]["user_id"] == 2 
#     assert notifications[1]["user_id"] == 1

#     order_id = response.json()["id"]

# def test_delete_notifications_pendingstatus(test_client):
#     client, temp_notif_db = test_client
#     new_order = {
#         "customer_id": 1,
#         "restaurant_id": 1,
#         "status": OrderStatus.PENDING.value,
#         "location": OrderLocation.BRITISH_COLUMBIA.value,
#         "order_items": [{
#             "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
#         }]
#     }
#     response = client.post("/orders/", json=new_order)
#     assert response.status_code == 200
#     order_id = response.json()["id"]

#     delete_response = client.delete(f"/orders/{order_id}")
#     assert delete_response.status_code == 200
#     notifications = json.loads(temp_notif_db.read_text())
#     assert len(notifications) == 4
#     assert notifications[2] ["user_id"] == 2
#     assert notifications[2] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[2] ["is_read"] == False
#     assert notifications[2] ["message"] == "Order with ID 1 has been cancelled by the customer before confirmation"
#     assert notifications[3] ["user_id"] == 1
#     assert notifications[3] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[3] ["is_read"] == False
#     assert notifications[3] ["message"] == "Order 1 has been successfully cancelled before confirmation"

# def test_delete_notifications_awaiting_payment_status(test_client):
#     client, temp_notif_db = test_client
#     new_order = {
#         "customer_id": 1,
#         "restaurant_id": 1,
#         "status": OrderStatus.AWAITING_PAYMENT.value,
#         "location": OrderLocation.BRITISH_COLUMBIA.value,
#         "order_items": [{
#             "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
#         }]
#     }
#     response = client.post("/orders/", json=new_order)
#     assert response.status_code == 200
#     order_id = response.json()["id"]
#     delete_response = client.delete(f"/orders/{order_id}")
#     assert delete_response.status_code == 200
#     notifications = json.loads(temp_notif_db.read_text())
#     assert len(notifications) == 4
#     assert notifications[2] ["user_id"] == 2
#     assert notifications[2] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[2] ["is_read"] == False
#     assert notifications[2] ["message"] == "Order with ID 1 has been cancelled by the customer before confirmation"
#     assert notifications[3] ["user_id"] == 1
#     assert notifications[3] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[3] ["is_read"] == False
#     assert notifications[3] ["message"] == "Order 1 has been successfully cancelled before confirmation"

# def test_delete_notifications_payment_failed_status(test_client):
#     client, temp_notif_db = test_client
#     new_order = {
#         "customer_id": 1,
#         "restaurant_id": 1,
#         "status": OrderStatus.PAYMENT_FAILED.value,
#         "location": OrderLocation.BRITISH_COLUMBIA.value,
#         "order_items": [{
#             "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
#         }]
#     }
#     response = client.post("/orders/", json=new_order)
#     assert response.status_code == 200
#     order_id = response.json()["id"]
#     delete_response = client.delete(f"/orders/{order_id}")
#     assert delete_response.status_code == 200
#     notifications = json.loads(temp_notif_db.read_text())
#     assert len(notifications) == 4
#     assert notifications[2] ["user_id"] == 2
#     assert notifications[2] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[2] ["is_read"] == False
#     assert notifications[2] ["message"] == "Customer's payment failed. Order with ID 1 has been cancelled."
#     assert notifications[3] ["user_id"] == 1
#     assert notifications[3] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[3] ["is_read"] == False
#     assert notifications[3] ["message"] == "Payment Failed. Please review payment method. Order 1 has been cancelled"

# def test_delete_notifications_preparing_status(test_client):
#     client, temp_notif_db = test_client
#     new_order = {
#         "customer_id": 1,
#         "restaurant_id": 1,
#         "status": OrderStatus.PREPARING_ORDER.value,
#         "location": OrderLocation.BRITISH_COLUMBIA.value,
#         "order_items": [{
#             "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
#         }]
#     }
#     response = client.post("/orders/", json=new_order)
#     assert response.status_code == 200
#     order_id = response.json()["id"]
#     delete_response = client.delete(f"/orders/{order_id}")
#     assert delete_response.status_code == 200
#     notifications = json.loads(temp_notif_db.read_text())
#     assert len(notifications) == 4
#     assert notifications[2] ["user_id"] == 2
#     assert notifications[2] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[2] ["is_read"] == False
#     assert notifications[2] ["message"] == "Order with ID 1 has been cancelled by the customer after confirmation, fees will be applied"
#     assert notifications[3] ["user_id"] == 1
#     assert notifications[3] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[3] ["is_read"] == False
#     assert notifications[3] ["message"] == "Order 1 has been cancelled after confirmation, fees will be applied"

# def test_delete_notifications_payment_confirmed_status(test_client):
#     client, temp_notif_db = test_client
#     new_order = {
#         "customer_id": 1,
#         "restaurant_id": 1,
#         "status": OrderStatus.PAYMENT_CONFIRMED.value,
#         "location": OrderLocation.BRITISH_COLUMBIA.value,
#         "order_items": [{
#             "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
#         }]
#     }
#     response = client.post("/orders/", json=new_order)
#     assert response.status_code == 200
#     order_id = response.json()["id"]
#     delete_response = client.delete(f"/orders/{order_id}")
#     assert delete_response.status_code == 200
#     notifications = json.loads(temp_notif_db.read_text())
#     assert len(notifications) == 4
#     assert notifications[2] ["user_id"] == 2
#     assert notifications[2] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[2] ["is_read"] == False
#     assert notifications[2] ["message"] == "Order with ID 1 has been cancelled by the customer after confirmation, fees will be applied"
#     assert notifications[3] ["user_id"] == 1
#     assert notifications[3] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[3] ["is_read"] == False
#     assert notifications[3] ["message"] == "Order 1 has been cancelled after confirmation, fees will be applied"

# def test_delete_notifications_out_for_delivery_status(test_client):
#     client, temp_notif_db = test_client
#     new_order = {
#         "customer_id": 1,
#         "restaurant_id": 1,
#         "status": OrderStatus.OUT_FOR_DELIVERY.value,
#         "location": OrderLocation.BRITISH_COLUMBIA.value,
#         "order_items": [{
#             "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
#         }]
#     }
#     response = client.post("/orders/", json=new_order)
#     assert response.status_code == 200
#     order_id = response.json()["id"]
#     delete_response = client.delete(f"/orders/{order_id}")
#     assert delete_response.status_code == 403
#     notifications = json.loads(temp_notif_db.read_text())
#     assert len(notifications) == 2

    
# def test_notification_new_item_added(test_client):
#     client, temp_notif_db = test_client
#     new_order = {
#         "customer_id": 1, 
#         "restaurant_id": 1,
#         "status": OrderStatus.PREPARING_ORDER.value,
#         "location": OrderLocation.BRITISH_COLUMBIA.value,
#         "order_items": [{
#             "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
#         }]
#     }
#     response = client.post("/orders/", json=new_order)
#     assert response.status_code == 200
#     order_id = response.json()["id"]

#     add_item_response = client.post(f"/orders/{order_id}/items",
#         params = {"quantity": 2},
#         json = {
#             "id": 101,
#             "name": "Test Item",
#             "description": "A test item",
#             "price": 5.0
#         }
#     )

#     assert add_item_response.status_code == 200
#     notifications = json.loads(temp_notif_db.read_text())
#     assert len(notifications) == 3
#     assert notifications[2] ["user_id"] == 2
#     assert notifications[2] ["type"] == NotificationType.NEW_ITEM_ADDED.value
#     assert notifications[2] ["is_read"] == False


# def test_full_order_notification(test_client):
#     client, temp_notif_db = test_client
#     new_order = {
#         "customer_id": 1,
#         "restaurant_id": 1,
#         "status": OrderStatus.PENDING.value,
#         "location": OrderLocation.BRITISH_COLUMBIA.value,
#         "order_items": [{
#             "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
#         }]
#     }

#     response = client.post("/orders/", json=new_order)
#     assert response.status_code == 200
#     order_id = response.json()["id"]

#     notifications = json.loads(temp_notif_db.read_text())
#     assert len(notifications) == 2
#     assert notifications[0] ["user_id"] == 2
#     assert notifications[0] ["type"] == NotificationType.NEW_ORDER_RECEIVED.value
#     assert notifications[0] ["is_read"] == False
#     assert notifications[0] ["message"] == "A new order with id 1 has been received."
#     assert notifications[1] ["user_id"] == 1
#     assert notifications[1] ["type"] == NotificationType.NEW_ORDER_RECEIVED.value
#     assert notifications[1] ["is_read"] == False
#     assert notifications[1] ["message"] == "Your order at Fake Rest has been received, and is awaiting payment"

#     add_item_response = client.post(f"/orders/{order_id}/items",
#         params = {"quantity": 2},
#         json = {
#             "id": 101,
#             "name": "Test Item",
#             "description": "A test item",
#             "price": 5.0
#         }
#     )
#     assert add_item_response.status_code == 200
#     notifications = json.loads(temp_notif_db.read_text())
#     assert len(notifications) == 3
#     assert notifications[2] ["user_id"] == 2
#     assert notifications[2] ["type"] == NotificationType.NEW_ITEM_ADDED.value
#     assert notifications[2] ["is_read"] == False
#     assert notifications[2] ["message"] == "Customer has added Test Item to order #1"

#     delete_response = client.delete(f"/orders/{order_id}")
#     assert delete_response.status_code == 200
#     notifications = json.loads(temp_notif_db.read_text())
#     assert len(notifications) == 5
#     assert notifications[3] ["user_id"] == 2
#     assert notifications[3] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[3] ["is_read"] == False
#     assert notifications[3] ["message"] == "Order with ID 1 has been cancelled by the customer before confirmation"
#     assert notifications[4] ["user_id"] == 1
#     assert notifications[4] ["type"] == NotificationType.ORDER_CANCELLED.value
#     assert notifications[4] ["is_read"] == False
#     assert notifications[4] ["message"] == "Order 1 has been successfully cancelled before confirmation"

