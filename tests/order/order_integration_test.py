import pytest
import json
from fastapi.testclient import TestClient
from src.backend.models.order import OrderStatus, OrderLocation
from src.backend.models.payment import PaymentOptions
from src.backend.routers.payments import get_controller as get_payment_controller
from src.backend.routers.transactions import get_controller as get_transaction_controller
from src.backend.models.user import Role
from src.backend.controllers.order_controller import OrderController
from src.backend.controllers.notification_controller import NotificationController
from src.backend.controllers.transaction_controller import TransactionController
from src.backend.controllers.payment_controller import PaymentController
from src.backend.repositories.order_repo import OrderRepository
from src.backend.repositories.notification_repo import NotificationRepository
from src.backend.repositories.user_repo import UserRepository
from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.repositories.transaction_repo import TransactionRepository
from src.backend.repositories.payment_repo import PaymentRepository
import src.backend.utils.auth_dependencies as auth_dependencies
from src.backend.routers.orders import get_controller
from src.backend.main import app
from src.backend.repositories.delivery_repo import DeliveryRepository
from src.backend.controllers.delivery_controller import DeliveryController
from src.backend.routers.deliveries import get_controller as get_delivery_controller

@pytest.fixture
def test_client(tmp_path):

    temp_db = tmp_path / "test.json"
    temp_notif_db = tmp_path / "test_notif.json"
    temp_restaurant_db = tmp_path / "test.restaurant.json"
    temp_transaction_db = tmp_path / "test.transaction.json"
    temp_payment_db = tmp_path / "test_payments.json"
    temp_user_db = tmp_path / "test_users.json"
    temp_delivery_db = tmp_path / "test_delivery.json"

    temp_db.write_text(json.dumps([]))
    temp_notif_db.write_text(json.dumps([]))
    temp_restaurant_db.write_text(json.dumps([]))
    temp_transaction_db.write_text(json.dumps([]))
    temp_delivery_db.write_text(json.dumps([]))

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
    test_notif_repo = NotificationRepository(file_path=str(temp_notif_db))
    test_restaurant_repo = RestaurantRepository(file_path=str(temp_restaurant_db))
    test_transaction_repo = TransactionRepository(file_path=str(temp_transaction_db))
    test_payment_repo = PaymentRepository(file_path=str(temp_payment_db))
    test_delivery_repo = DeliveryRepository(file_path=str(temp_delivery_db))

    test_delivery_controller = DeliveryController(repo=test_delivery_repo, order_repo=test_repo)
    test_notif_controller = NotificationController(repo=test_notif_repo)
    test_payment_controller = PaymentController(repo=test_payment_repo)
    
    test_transaction_controller = TransactionController(
        payment_repo=test_payment_repo, 
        repo=test_transaction_repo, 
        notif_controller=test_notif_controller
    )
    test_controller = OrderController(
        repo=test_repo, 
        notif_controller=test_notif_controller,
        delivery_controller=test_delivery_controller
    )
    test_controller.restaurant_repo = test_restaurant_repo

    
    app.dependency_overrides[get_controller] = lambda: test_controller
    app.dependency_overrides[get_payment_controller] = lambda: test_payment_controller
    app.dependency_overrides[get_transaction_controller] = lambda: test_transaction_controller
    app.dependency_overrides[get_delivery_controller] = lambda: test_delivery_controller

    original_repo = auth_dependencies.repo
    auth_dependencies.repo = test_user_repo

    client = TestClient(app)
    client.headers.update({"X-User-Id": "1"})

    yield client, temp_notif_db, test_transaction_controller, test_payment_controller, test_delivery_controller


    auth_dependencies.repo = original_repo
    app.dependency_overrides.clear()

def test_full_order_integration(test_client):
    client, temp_notif_db, test_transaction_controller, test_payment_controller, test_delivery_controller = test_client

    order_id = 1
    new_order = {
        "customer_id": 1,
        "restaurant_id": 1,
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [{
            "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
        }]
    }

    '''
    menu_item = {
        "name": "Test Menu Item",
        "description": "A menu item for testing",
        "price": 10,
        "id": 1
    }
    
    add_item_response = client.post(f"/orders/{order_id}/items",params = {"quantity": 1},json = menu_item)
    assert add_item_response.status_code == 200
    '''

    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_price = response.json()["total_price"]

    card_payment = {
    "user_id": 1,
    "method": PaymentOptions.CREDIT_CARD.value,
    "card_digits": "4234567812345678",
    "expiration_month": 12,
    "expiration_year": 2048,
    "CVV": "123",
    "name_on_card": "Umberto De Luca"
    }

    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response = client.post("/payment/card", params={"active": True}, json=card_payment) 
    assert payment_response.status_code == 200
    payment_id = payment_response.json()["id"]

    transaction_payload = {
        "payment_method_id": payment_id,
        "order_id": order_id,
        "amount": order_price
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    transaction_response = client.post("/transaction/", json=transaction_payload)
    assert transaction_response.status_code == 200
    transaction_approved = transaction_response.json()["is_successful"]
    assert transaction_approved

    updated_order_response = client.put(f"/orders/{order_id}/status", params={"new_status": OrderStatus.AWAITING_PAYMENT.value, "role": "manager", "transaction_is_successful": transaction_approved})
    assert updated_order_response.status_code == 200

    updated_order_response = client.put(f"/orders/{order_id}/status", params={"new_status": OrderStatus.OUT_FOR_DELIVERY.value, "role": "manager"})
    assert updated_order_response.status_code == 200

    get_delivery_response = client.get(f"/deliveries/order/{order_id}")
    assert get_delivery_response.status_code == 200

    data = get_delivery_response.json()
    assert data["id"] == 1
    assert data["order_id"] == 1
    assert data["driver_id"] == 1
    assert "assigned_at" in data

    updated_order_response = client.put(f"/orders/{order_id}/status", params={"new_status": OrderStatus.DELIVERED.value, "role": "manager"})
    assert updated_order_response.status_code == 200

    get_delivery_response = client.get(f"/deliveries/order/{order_id}")
    assert get_delivery_response.status_code == 200

    data = get_delivery_response.json()
    assert ["delivered_at"] is not None



