import pytest, json
from fastapi.testclient import TestClient
from unittest.mock import patch, ANY
from src.backend.services.email_service import EmailService
from src.backend.models.user import Role
from src.backend.models.order import OrderStatus, OrderLocation
from src.backend.controllers.order_controller import OrderController
from src.backend.controllers.delivery_controller import DeliveryController
from src.backend.controllers.notification_controller import NotificationController
from src.backend.controllers.delivery_controller import DeliveryController
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
                "email": "invalidEmail",
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
    test_deliv_controller = DeliveryController(repo=test_deliv_repo)

    test_controller = OrderController(
        repo=test_repo, 
        notif_controller=test_notif_controller,
        delivery_controller=test_deliv_controller
    )
    test_controller.restaurant_repo = test_restaurant_repo
    test_controller.user_repo = test_user_repo
    test_deliv_controller.order_repo = test_repo


    app.dependency_overrides[get_controller] = lambda: test_controller
    app.dependency_overrides[get_delivery_controller] = lambda: test_deliv_controller

    original_repo = auth_dependencies.repo
    auth_dependencies.repo = test_user_repo

    client = TestClient(app)
    client.headers.update({"X-User-Id": "1"})

    yield client


    auth_dependencies.repo = original_repo
    app.dependency_overrides.clear()


def test_email_sent_on_delivery(test_client):
    client = test_client

    with patch("src.backend.services.email_service.EmailService.send_email") as mock_email:
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

        client.put(f"/orders/{order_id}/status",
            params={"new_status": OrderStatus.OUT_FOR_DELIVERY.value, "role": "manager"}
        )
        client.put(f"/orders/{order_id}/status",
            params={"new_status": OrderStatus.DELIVERED.value, "role": "manager"}
        )

        mock_email.assert_called_once_with("testcustomer@123.com", "Order has been delivered", ANY)




def test_unsuccessful_email_sent_on_delivery(test_client, mocker):
    client = test_client

    client = test_client

    with patch("src.backend.services.email_service.EmailService.send_email") as mock_email:
        mock_email.side_effect = Exception("SMTP error")

        new_order = {
            "customer_id": 3,
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

        client.put(f"/orders/{order_id}/status",
            params={"new_status": OrderStatus.OUT_FOR_DELIVERY.value, "role": "manager"}
        )
        delivered_response = client.put(f"/orders/{order_id}/status",
            params={"new_status": OrderStatus.DELIVERED.value, "role": "manager"}
        )
        assert delivered_response.status_code == 200
        mock_email.assert_called_once()
    