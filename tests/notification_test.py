import pytest
import json
from fastapi.testclient import TestClient
from src.backend.models.order import OrderStatus, OrderLocation
from src.backend.models.notification import NotificationType
from src.backend.models.payment import PaymentOptions
from src.backend.models.payment_transaction import PaymentTransactionCreate
from src.backend.models.card_payment import CardPaymentBrand
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
    
    temp_payment_db.write_text(json.dumps([{
        "user_id": 1,
        "method": "cash",
        "is_active": True,
        "id": 1
    },
    {
        "user_id": 1,
        "method": PaymentOptions.CREDIT_CARD.value,
        "card_digits": "4234567812345678",
        "expiration_month": 4,
        "expiration_year": 2026,
        "CVV": "123",
        "name_on_card": "Monkey D Luffy",
        "card_brand": CardPaymentBrand.VISA.value,
        "id": 2
    },
    {
        "user_id": 1,
        "method": PaymentOptions.CREDIT_CARD.value,
        "card_digits": "4234567812345678",
        "expiration_month": 1,
        "expiration_year": 2025,
        "CVV": "123",
        "name_on_card": "Monkey D Luffy",
        "card_brand": CardPaymentBrand.VISA.value,
        "id": 3
    }
    ]))

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
    
    transaction_controller = TransactionController(
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
    original_repo = auth_dependencies.repo
    auth_dependencies.repo = test_user_repo

    client = TestClient(app)
    client.headers.update({"X-User-Id": "1"})

    yield client, temp_notif_db, transaction_controller, test_payment_controller, test_delivery_controller


    auth_dependencies.repo = original_repo
    app.dependency_overrides.clear()


def test_add_order_notifications(test_client):
    client, temp_notif_db, transaction_controller, test_payment_controller, test_delivery_controller = test_client
    new_order = {
        "customer_id": 1,
        "restaurant_id": 1,
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 2
    assert notifications[0]["user_id"] == 2 
    assert notifications[1]["user_id"] == 1

    order_id = response.json()["id"]

def test_delete_notifications_pendingstatus(test_client):
    client, temp_notif_db, transaction_controller, test_payment_controller, test_delivery_controller = test_client
    new_order = {
        "customer_id": 1,
        "restaurant_id": 1,
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [{
            "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
        }]
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    delete_response = client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 4
    assert notifications[2] ["user_id"] == 2
    assert notifications[2] ["type"] == NotificationType.ORDER_CANCELLED.value
    assert notifications[2] ["is_read"] == False
    assert notifications[3] ["user_id"] == 1
    assert notifications[3] ["type"] == NotificationType.ORDER_CANCELLED.value
    assert notifications[3] ["is_read"] == False

    

def test_delete_notifications_preparingstatus(test_client):
    client, temp_notif_db, transaction_controller, test_payment_controller, test_delivery_controller = test_client

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
    delete_response = client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 4
    assert notifications[2] ["user_id"] == 2
    assert notifications[2] ["type"] == NotificationType.ORDER_CANCELLED.value
    assert notifications[2] ["is_read"] == False
    assert notifications[3] ["user_id"] == 1
    assert notifications[3] ["type"] == NotificationType.ORDER_CANCELLED.value
    assert notifications[3] ["is_read"] == False

def test_notification_update_order_status(test_client):
    client, temp_notif_db, transaction_controller, test_payment_controller, test_delivery_controller = test_client
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
    assert notifications[3] ["user_id"] == 2
    assert notifications[3] ["type"] == NotificationType.ORDER_IN_TRANSIT.value
    assert notifications[3] ["is_read"] == False


def test_notification_new_item_added(test_client):
    client, temp_notif_db, transaction_controller, test_payment_controller, test_delivery_controller = test_client
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

    add_item_response = client.post(f"/orders/{order_id}/items",
        params = {"quantity": 2},
        json = {
            "id": 101,
            "name": "Test Item",
            "description": "A test item",
            "price": 5.0
        }
    )

    assert add_item_response.status_code == 200
    notifications = json.loads(temp_notif_db.read_text())
    assert len(notifications) == 3
    assert notifications[2] ["user_id"] == 2
    assert notifications[2] ["type"] == NotificationType.NEW_ITEM_ADDED.value
    assert notifications[2] ["is_read"] == False

def test_successful_cash_transaction_notif(test_client):
    client, temp_notif_db, transaction_controller, test_payment_controller, test_delivery_controller = test_client
    new_order = {
        "customer_id": 1, 
        "restaurant_id": 1,
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [{
            "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
        }]
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]
    

    transaction = PaymentTransactionCreate(
        payment_method_id = 1,
        order_id = order_id,
        amount = 1.10
    )
    
    transaction_controller.create_transaction(transaction)

    notifications = json.loads(temp_notif_db.read_text())
    assert notifications[2] ["user_id"] == 1
    assert notifications[2] ["type"] == NotificationType.ORDER_IN_PROGRESS.value
    assert notifications[2] ["is_read"] == False
    assert notifications[2] ["message"] == "Your cash payment for order 1 was successful"


def test_successful_card_transaction_notif(test_client):
    client, temp_notif_db, transaction_controller, test_payment_controller, test_delivery_controller = test_client
    new_order = {
        "customer_id": 1, 
        "restaurant_id": 1,
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [{
            "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
        }]
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]
    

    transaction = PaymentTransactionCreate(
        payment_method_id = 2,
        order_id = order_id,
        amount = 1.10
    )
    
    transaction_controller.create_transaction(transaction)

    notifications = json.loads(temp_notif_db.read_text())
    assert notifications[2] ["user_id"] == 1
    assert notifications[2] ["type"] == NotificationType.ORDER_IN_PROGRESS.value
    assert notifications[2] ["is_read"] == False
    assert notifications[2] ["message"] == "Your card payment for order 1 was successful"

def test_unsuccessful_transaction_notif(test_client):
    client, temp_notif_db, transaction_controller, test_payment_controller, test_delivery_controller = test_client
    new_order = {
        "customer_id": 1, 
        "restaurant_id": 1,
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [{
            "item_id": 101, "quantity": 2, "price_at_purchase": 5.0
        }]
    }
    response = client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]
    

    transaction = PaymentTransactionCreate(
        payment_method_id = 3,
        order_id = order_id,
        amount = 1.10
    )
    transaction_controller.create_transaction(transaction)
    notifications = json.loads(temp_notif_db.read_text())
    assert notifications[2] ["user_id"] == 1
    assert notifications[2] ["type"] == NotificationType.PAYMENT_FAILED.value
    assert notifications[2] ["is_read"] == False
    assert notifications[2] ["message"] == "Your payment for order 1 has been declined"