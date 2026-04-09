import pytest
import json
from fastapi.testclient import TestClient
from src.backend.models.order import OrderStatus, OrderLocation
from src.backend.models.notification import NotificationType
from src.backend.models.user import Role
from src.backend.controllers.order_controller import OrderController
from src.backend.controllers.delivery_controller import DeliveryController
from src.backend.controllers.notification_controller import NotificationController
from src.backend.repositories.order_repo import OrderRepository
from src.backend.repositories.notification_repo import NotificationRepository
from src.backend.repositories.delivery_repo import DeliveryRepository
from src.backend.repositories.user_repo import UserRepository
from src.backend.repositories.restaurant_repo import RestaurantRepository
import src.backend.utils.auth_dependencies as auth_dependencies
from src.backend.routers.orders import get_controller
from src.backend.routers.deliveries import get_controller as get_delivery_controller
from src.backend.main import app



@pytest.fixture
def test_client(tmp_path):

    temp_db = tmp_path / "test.json"
    temp_notif_db = tmp_path / "test_notif.json"
    temp_restaurant_db = tmp_path / "test.restaurant.json"
    temp_user_db = tmp_path / "test_users.json"
    temp_deliv_db = tmp_path / "test_deliv_db.json"

    temp_db.write_text(json.dumps([]))
    temp_notif_db.write_text(json.dumps([]))
    temp_restaurant_db.write_text(json.dumps([]))
    temp_deliv_db.write_text(json.dumps([]))

    temp_user_db.write_text(json.dumps({
        "Users": [
            {
                "id": 1,
                "username": "TestCustomer",
                "email": "testcustomer@123.com",
                "password": "Test@123",
                "role": Role.CUSTOMER.value, 
                "is_logged_in": False,
                "is_blocked": False
            },
            {
                "id": 2,
                "username": "TestOwner",
                "email": "testowner@123.com",
                "password": "Test@123",
                "role": Role.RESTAURANT_OWNER.value,
                "is_logged_in": False,
                "is_blocked": False
            },
            {
                "id": 3,
                "username": "TestAdmin",
                "email": "testadmin@123.com",
                "password": "Test@123",
                "role": Role.ADMIN.value,
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

    test_repo = OrderRepository(file_path=str(temp_db))
    test_deliv_repo = DeliveryRepository(file_path=str(temp_deliv_db))
    test_notif_repo = NotificationRepository(file_path=str(temp_notif_db))
    test_restaurant_repo = RestaurantRepository(file_path=str(temp_restaurant_db))

    test_notif_controller = NotificationController(repo=test_notif_repo)
    test_deliv_controller = DeliveryController(repo=test_deliv_repo, order_repo=test_repo)

    test_controller = OrderController(
        repo=test_repo, 
        notif_controller=test_notif_controller,
        delivery_controller=test_deliv_controller
    )
    test_controller.restaurant_repo = test_restaurant_repo

    

    app.dependency_overrides[get_controller] = lambda: test_controller
    app.dependency_overrides[get_delivery_controller] = lambda: test_deliv_controller

    original_repo = auth_dependencies.repo
    auth_dependencies.repo = test_user_repo

    client = TestClient(app)
    client.headers.update({"X-User-Id": "1"})

    yield client, temp_notif_db


    auth_dependencies.repo = original_repo
    app.dependency_overrides.clear()


def test_notification_status_payment_confirmed(test_client):
    client, temp_notif_db = test_client
    new_order = {
        "customer_id": 1,
        "restaurant_id": 1,
        "status": OrderStatus.AWAITING_PAYMENT.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [{
            "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
        }]
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    update_response = client.put(f"/orders/{order_id}/status",
        params={
            "new_status": OrderStatus.PAYMENT_CONFIRMED.value,
            "role": "manager",
            "transaction_is_successful": True
        }
    )
    assert update_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 3
    assert notifications[2] ["user_id"] == 1
    assert notifications[2] ["type"] == NotificationType.ORDER_CONFIRMED.value
    assert notifications[2] ["is_read"] == False
    assert notifications[2] ["message"] == "Your order status is now payment confirmed"

def test_notification_status_payment_failed(test_client):
    client, temp_notif_db = test_client
    new_order = {
        "customer_id": 1,
        "restaurant_id": 1,
        "status": OrderStatus.AWAITING_PAYMENT.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [{
            "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
        }]
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    update_response = client.put(f"/orders/{order_id}/status",
        params={
            "new_status": OrderStatus.AWAITING_PAYMENT.value,
            "role": "manager",
            "transaction_is_successful": False
        }
    )
    assert update_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 3
    assert notifications[2] ["user_id"] == 1
    assert notifications[2] ["type"] == NotificationType.PAYMENT_FAILED.value
    assert notifications[2] ["is_read"] == False
    assert notifications[2] ["message"] == "Your order status is now payment failed"


def test_notification_status_preparing_order(test_client):
    client, temp_notif_db = test_client
    new_order = {
        "customer_id": 1,
        "restaurant_id": 1,
        "status": OrderStatus.PAYMENT_CONFIRMED.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [{
            "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
        }]
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    update_response = client.put(f"/orders/{order_id}/status",
        params={
            "new_status": OrderStatus.PREPARING_ORDER.value,
            "role": "manager"
        }
    )
    assert update_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 3
    assert notifications[2] ["user_id"] == 1
    assert notifications[2] ["type"] == NotificationType.ORDER_IN_PROGRESS.value
    assert notifications[2] ["is_read"] == False
    assert notifications[2] ["message"] == "Your order status is now preparing"

def test_notification_status_out_for_delivery(test_client):
    client, temp_notif_db = test_client
    new_order = {
        "customer_id": 1,
        "restaurant_id": 1,
        "status": OrderStatus.PREPARING_ORDER.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [{
            "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
        }]
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    update_response = client.put(f"/orders/{order_id}/status",
        params={
            "new_status": OrderStatus.OUT_FOR_DELIVERY.value,
            "role": "manager"
        }
    )
    assert update_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 4
    assert notifications[2] ["user_id"] == 1
    assert notifications[2] ["type"] == NotificationType.ORDER_IN_TRANSIT.value
    assert notifications[2] ["is_read"] == False
    assert notifications[2] ["message"] == "Your order status is now out for delivery"
    assert notifications[3] ["user_id"] == 2
    assert notifications[3] ["type"] == NotificationType.ORDER_IN_TRANSIT.value
    assert notifications[3] ["is_read"] == False
    assert notifications[3] ["message"] == "Order #1 picked up by driver"

def test_notification_status_delivered(test_client):
    client, temp_notif_db = test_client
    new_order = {
        "customer_id": 1,
        "restaurant_id": 1,
        "status": OrderStatus.PREPARING_ORDER.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [{
            "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
        }]
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    update_response = client.put(f"/orders/{order_id}/status",
        params={
            "new_status": OrderStatus.OUT_FOR_DELIVERY.value,
            "role": "manager"
        }
    )
    update_response = client.put(f"/orders/{order_id}/status",
        params={
            "new_status": OrderStatus.DELIVERED.value,
            "role": "manager"
        }
    )
    print(update_response.json())
    assert update_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 6
    assert notifications[4] ["user_id"] == 1
    assert notifications[4] ["type"] == NotificationType.ORDER_DELIVERED.value
    assert notifications[4] ["is_read"] == False
    assert notifications[4] ["message"] == "Your order status is now delivered"
    assert notifications[5] ["user_id"] == 2
    assert notifications[5] ["type"] == NotificationType.ORDER_DELIVERED.value
    assert notifications[5] ["is_read"] == False
    assert notifications[5] ["message"] == "Order #1 has been delivered"


def test_notification_status_chain(test_client):
    client, temp_notif_db = test_client
    new_order = {
        "customer_id": 1,
        "restaurant_id": 1,
        "status": OrderStatus.AWAITING_PAYMENT.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [{
            "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
        }]
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    update_response = client.put(f"/orders/{order_id}/status",
        params={
            "new_status": OrderStatus.PAYMENT_CONFIRMED.value,
            "role": "manager",
            "transaction_is_successful": True
        }
    )
    assert update_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 3
    assert notifications[2] ["user_id"] == 1
    assert notifications[2] ["type"] == NotificationType.ORDER_CONFIRMED.value
    assert notifications[2] ["is_read"] == False
    assert notifications[2] ["message"] == "Your order status is now payment confirmed"

    update_response = client.put(f"/orders/{order_id}/status",
        params={
            "new_status": OrderStatus.PREPARING_ORDER.value,
            "role": "manager"
        }
    )
    assert update_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 4
    assert notifications[3] ["user_id"] == 1
    assert notifications[3] ["type"] == NotificationType.ORDER_IN_PROGRESS.value
    assert notifications[3] ["is_read"] == False
    assert notifications[3] ["message"] == "Your order status is now preparing"

    update_response = client.put(f"/orders/{order_id}/status",
        params={
            "new_status": OrderStatus.OUT_FOR_DELIVERY.value,
            "role": "manager"
        }
    )
    assert update_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 6
    assert notifications[4] ["user_id"] == 1
    assert notifications[4] ["type"] == NotificationType.ORDER_IN_TRANSIT.value
    assert notifications[4] ["is_read"] == False
    assert notifications[4] ["message"] == "Your order status is now out for delivery"
    assert notifications[5] ["user_id"] == 2
    assert notifications[5] ["type"] == NotificationType.ORDER_IN_TRANSIT.value
    assert notifications[5] ["is_read"] == False
    assert notifications[5] ["message"] == "Order #1 picked up by driver"

    update_response = client.put(f"/orders/{order_id}/status",
        params={
            "new_status": OrderStatus.DELIVERED.value,
            "role": "manager"
        }
    )
    assert update_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 8
    assert notifications[6] ["user_id"] == 1
    assert notifications[6] ["type"] == NotificationType.ORDER_DELIVERED.value
    assert notifications[6] ["is_read"] == False
    assert notifications[6] ["message"] == "Your order status is now delivered"
    assert notifications[7] ["user_id"] == 2
    assert notifications[7] ["type"] == NotificationType.ORDER_DELIVERED.value
    assert notifications[7] ["is_read"] == False
    assert notifications[7] ["message"] == "Order #1 has been delivered"