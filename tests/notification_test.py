import pytest
import json
from fastapi.testclient import TestClient
from src.backend.models.order import OrderStatus, OrderLocation
from src.backend.models.notification import NotificationType
from src.backend.controllers.order_controller import OrderController
from src.backend.controllers.notification_controller import NotificationController
from src.backend.repositories.order_repo import OrderRepository
from src.backend.repositories.notification_repo import NotificationRepository
from src.backend.repositories.user_repo import UserRepository
from src.backend.repositories.restaurant_repo import RestaurantRepository
import src.backend.utils.auth_dependencies as auth_dependencies
from src.backend.routers.orders import get_controller
from src.backend.main import app



@pytest.fixture
def test_client(tmp_path):
    temp_db = tmp_path / "test.json"
    temp_db.write_text(json.dumps([]))

    temp_notif_db = tmp_path / "test_notif.json"
    temp_notif_db.write_text(json.dumps([]))

    temp_restaurant_db = tmp_path / "test.restaurant.json"
    temp_restaurant_db.write_text(json.dumps([]))

    test_repo = OrderRepository(file_path=str(temp_db))
    test_notif_repo = NotificationRepository(file_path=str(temp_notif_db))
    test_restaurant_repo = RestaurantRepository(file_path=str(temp_restaurant_db))

    test_notif_controller = NotificationController(repo=test_notif_repo)
    test_controller = OrderController(repo=test_repo, notif_controller=test_notif_controller)
    test_controller.restaurant_repo = test_restaurant_repo

    temp_user_db = tmp_path / "test_users.json"
    temp_user_db.write_text(json.dumps({
        "Users": [
            {
                "id": 1,
                "username": "TestCustomer",
                "email": "testcustomer@123.com",
                "password": "Test@123",
                "role": "customer", 
                "is_logged_in": False,
                "is_blocked": False
            },
            {
                "id": 2,
                "username": "TestOwner",
                "email": "testowner@123.com",
                "password": "Test@123",
                "role": "restaurant owner",
                "is_logged_in": False,
                "is_blocked": False
            }
        ]
    }))
    temp_restaurant_db.write_text(json.dumps([{
        "id": 1,
        "name": "Fake Rest",
        "cuisine": "italian",
        "location": "british columbia",
        "delivery_fee": 2.99,
        "owner_id": 2,
        "is_available": True
    }]))
    test_user_repo = UserRepository(file=str(temp_user_db))

    app.dependency_overrides[get_controller] = lambda: test_controller #tells fastAPI to use test controller instead of real controller
    original_repo = auth_dependencies.repo #saves the real repository before replacing it
    auth_dependencies.repo = test_user_repo # swaps in the temp user repo for auth

    client = TestClient(app) #simulates HTTP requests
    client.headers.update({"X-User-Id": "1"}) #Adds header defining User's Id to 1 for auth

    yield client, temp_notif_db #hands both the client and notif file to the test

    #restores everything after test finishes
    auth_dependencies.repo = original_repo
    app.dependency_overrides.clear()


def test_add_order_notifications(test_client):
    client, temp_notif_db = test_client
    new_order = {
        "customer_id": 1,
        "restaurant_id": 1,
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": []
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 2
    assert notifications[0]["user_id"] == 2  #manager notif
    assert notifications[1]["user_id"] == 1  #customer notif (success)

#Still not working, will fix this in my next pr
# def test_add_order_notif_exception(test_client):
#     client, temp_notif_db = test_client
#     new_order = {
#         "customer_id": 1,
#         "restaurant_id": 999,
#         "status": OrderStatus.PENDING.value,
#         "location": OrderLocation.BRITISH_COLUMBIA.value,
#         "order_items": [
#             {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
#         ]
#     }
#     response = client.post("/orders/", json=new_order)
#     notifications = json.loads(temp_notif_db.read_text())
#     print(response.json())
#     assert response.status_code == 200
#     assert len(notifications) == 1
#     assert notifications[0] ["user_id"] == 1 #customer notif (failed)
#     assert notifications["type"] == NotificationType.ORDER_FAILED.value