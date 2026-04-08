import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.payments import get_controller as get_payment_controller
from src.backend.routers.transactions import get_controller as get_transaction_controller
from src.backend.models.payment import PaymentOptions
from src.backend.repositories.transaction_repo import TransactionRepository
from src.backend.repositories.payment_repo import PaymentRepository
from src.backend.controllers.transaction_controller import TransactionController
from src.backend.controllers.payment_controller import PaymentController
from src.backend.repositories.notification_repo import NotificationRepository
from src.backend.controllers.notification_controller import NotificationController

@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real
    data/transaction.json & data/payment.json.  The temp file is deleted automatically after each
    test, so the production database is never touched.
    """
    temp_payment_db = tmp_path / "test_payment.json"
    temp_transaction_db = tmp_path / "test_transaction.json"
    temp_notif_db = tmp_path / "test_notifications.json"
    
    temp_notif_db.write_text(json.dumps([]))
    temp_payment_db.write_text(json.dumps([]))
    temp_transaction_db.write_text(json.dumps([]))

    shared_payment_repo = PaymentRepository(file_path=str(temp_payment_db))
    transaction_repo = TransactionRepository(file_path=str(temp_transaction_db))
    test_notif_repo = NotificationRepository(file_path=str(temp_notif_db))

    payment_controller = PaymentController(repo=shared_payment_repo)
    notification_controller = NotificationController(repo=test_notif_repo)
    transaction_controller = TransactionController(payment_repo=shared_payment_repo, repo=transaction_repo, notif_controller=notification_controller)

    app.dependency_overrides[get_payment_controller] = lambda: payment_controller
    app.dependency_overrides[get_transaction_controller] = lambda: transaction_controller

    with TestClient(app) as client:
        client.transaction_repo = transaction_repo
        yield client

    app.dependency_overrides.clear()

cash_payment = {
    "user_id": 1,
    "method": PaymentOptions.CASH.value
}

card_payment = {
    "user_id": 1,
    "method": PaymentOptions.CREDIT_CARD.value,
    "card_digits": "4234567812345678",
    "expiration_month": 12,
    "expiration_year": 2028,
    "CVV": "123",
    "name_on_card": "Umberto De Luca"
}

def test_create_transaction_with_invalid_fields(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response = test_client.post("/payment/cash", params={"active": True}, json=cash_payment) 
    assert payment_response.status_code == 200
    payment_id = payment_response.json()["id"]

    transaction_payload = {
        "payment_method_id": payment_id
    }

    # Should return 422 since the transaction has not the correct fields for TransactionCreate
    response = test_client.post("/transaction/", json=transaction_payload)
    assert response.status_code == 422

def test_create_cash_transaction(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response = test_client.post("/payment/cash", params={"active": True}, json=cash_payment) 
    assert payment_response.status_code == 200
    payment_id = payment_response.json()["id"]

    transaction_payload = {
        "payment_method_id": payment_id,
        "order_id": 15,
        "amount": 45.50
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    response = test_client.post("/transaction/", json=transaction_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["payment_method_id"] == payment_id
    assert data["order_id"] == 15
    assert data["amount"] == 45.50
    assert data["is_successful"] is True
    assert "id" in data

def test_create_invalid_cash_transaction(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response = test_client.post("/payment/cash", params={"active": True}, json=cash_payment) 
    assert payment_response.status_code == 200
    payment_id = 999

    transaction_payload = {
        "payment_method_id": payment_id,
        "order_id": 15,
        "amount": 45.50
    }

    # Since now payment id exists with id == 999, the transaction should give a 500 status code (no payment id was found for payment id == 999)
    response = test_client.post("/transaction/", json=transaction_payload)
    assert response.status_code == 500

def test_create_card_transaction(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response = test_client.post("/payment/card", params={"active": True}, json=card_payment) 
    assert payment_response.status_code == 200
    payment_id = payment_response.json()["id"]

    transaction_payload = {
        "payment_method_id": payment_id,
        "order_id": 10,
        "amount": 25.50
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    response = test_client.post("/transaction/", json=transaction_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["payment_method_id"] == payment_id
    assert data["order_id"] == 10
    assert data["amount"] == 25.50
    assert data["is_successful"] is True
    assert "id" in data

def test_create_invalid_card_transaction(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response = test_client.post("/payment/card", params={"active": True}, json=card_payment) 
    assert payment_response.status_code == 200
    payment_id = 999

    transaction_payload = {
        "payment_method_id": payment_id,
        "order_id": 10,
        "amount": 25.50
    }

    # Since now payment id exists with id == 999, the transaction should give a 500 status code (no payment id was found for payment id == 999)
    response = test_client.post("/transaction/", json=transaction_payload)
    assert response.status_code == 500

def test_delete_card_transaction(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response = test_client.post("/payment/card", params={"active": True}, json=card_payment) 
    assert payment_response.status_code == 200
    payment_id = payment_response.json()["id"]

    transaction_payload = {
        "payment_method_id": payment_id,
        "order_id": 10,
        "amount": 25.50
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    response = test_client.post("/transaction/", json=transaction_payload)
    assert response.status_code == 200
    transaction_id = response.json()["id"]

    # Delete transaction
    delete_response = test_client.delete(f"/transaction/{transaction_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the transaction should return a 404
    get_response = test_client.get(f"/transaction/{transaction_id}")
    assert get_response.status_code == 404

def test_delete_cash_transaction(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response = test_client.post("/payment/cash", params={"active": True}, json=cash_payment) 
    assert payment_response.status_code == 200
    payment_id = payment_response.json()["id"]

    transaction_payload = {
        "payment_method_id": payment_id,
        "order_id": 10,
        "amount": 25.50
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    response = test_client.post("/transaction/", json=transaction_payload)
    assert response.status_code == 200
    transaction_id = response.json()["id"]

    # Delete transaction
    delete_response = test_client.delete(f"/transaction/{transaction_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the transaction should return a 404
    get_response = test_client.get(f"/transaction/{transaction_id}")
    assert get_response.status_code == 404

def test_delete_transaction_with_invalid_id(test_client):
    transaction_id = 999

    # Delete transaction should retrieve 404 since no transaction is found with id == 999
    delete_response = test_client.delete(f"/transaction/{transaction_id}")
    assert delete_response.status_code == 404

def test_get_card_transaction_by_id(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response = test_client.post("/payment/card", params={"active": True}, json=card_payment) 
    assert payment_response.status_code == 200
    payment_id = payment_response.json()["id"]

    transaction_payload = {
        "payment_method_id": payment_id,
        "order_id": 10,
        "amount": 25.50
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    response = test_client.post("/transaction/", json=transaction_payload)
    assert response.status_code == 200
    transaction_id = response.json()["id"]

    # Now try to retrieve transaction
    get_response = test_client.get(f"/transaction/{transaction_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["payment_method_id"] == transaction_payload["payment_method_id"]
    assert data["order_id"] == transaction_payload["order_id"]
    assert data["is_successful"] == True
    assert "id" in data

def test_get_cash_transaction_by_id(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response = test_client.post("/payment/cash", params={"active": True}, json=cash_payment) 
    assert payment_response.status_code == 200
    payment_id = payment_response.json()["id"]

    transaction_payload = {
        "payment_method_id": payment_id,
        "order_id": 10,
        "amount": 25.50
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    response = test_client.post("/transaction/", json=transaction_payload)
    assert response.status_code == 200
    transaction_id = response.json()["id"]

    # Now try to retrieve transaction
    get_response = test_client.get(f"/transaction/{transaction_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["payment_method_id"] == transaction_payload["payment_method_id"]
    assert data["order_id"] == transaction_payload["order_id"]
    assert data["is_successful"] == True
    assert "id" in data

def test_get_transaction_by_invalid_id(test_client):
    transaction_id = 999

    # Now try to retrieve transaction should give a 404 since no transaction exists with that id
    get_response = test_client.get(f"/transaction/{transaction_id}")
    assert get_response.status_code == 404

def test_get_all_transactions_by_user_id(test_client):
    # First add payment methods
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response_1 = test_client.post("/payment/cash", params={"active": True}, json=cash_payment) 
    assert payment_response_1.status_code == 200
    payment_id_1 = payment_response_1.json()["id"]

    transaction_payload_1 = {
        "payment_method_id": payment_id_1,
        "order_id": 10,
        "amount": 25.50
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    response_1 = test_client.post("/transaction/", json=transaction_payload_1)
    assert response_1.status_code == 200
    transaction_id_1 = response_1.json()["id"]

    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response_2 = test_client.post("/payment/card", params={"active": True}, json=card_payment) 
    assert payment_response_2.status_code == 200
    payment_id_2 = payment_response_2.json()["id"]

    transaction_payload_2 = {
        "payment_method_id": payment_id_2,
        "order_id": 10,
        "amount": 25.50
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    response_2 = test_client.post("/transaction/", json=transaction_payload_2)
    assert response_2.status_code == 200
    transaction_id_2 = response_2.json()["id"]

    # All responses should have the same user_id
    user_id = response_1.json()["user_id"]

    # Now try to retrieve transactions
    get_response = test_client.get(f"/transaction/user_transactions/{user_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data) == 2
    assert data[0]["id"] == transaction_id_1
    assert data[1]["id"] == transaction_id_2

def test_get_all_transactions_by_invalid_user_id(test_client):
    # First add payment methods
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response_1 = test_client.post("/payment/cash", params={"active": True}, json=cash_payment) 
    assert payment_response_1.status_code == 200
    payment_id_1 = payment_response_1.json()["id"]

    transaction_payload_1 = {
        "payment_method_id": payment_id_1,
        "order_id": 10,
        "amount": 25.50
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    response_1 = test_client.post("/transaction/", json=transaction_payload_1)
    assert response_1.status_code == 200

    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response_2 = test_client.post("/payment/card", params={"active": True}, json=card_payment) 
    assert payment_response_2.status_code == 200
    payment_id_2 = payment_response_2.json()["id"]

    transaction_payload_2 = {
        "payment_method_id": payment_id_2,
        "order_id": 10,
        "amount": 25.50
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    response_2 = test_client.post("/transaction/", json=transaction_payload_2)
    assert response_2.status_code == 200

    user_id = 999

    # Now try to retrieve transactions should give 404 since no transactions exists for user_id == 999
    get_response = test_client.get(f"/transaction/user_transactions/{user_id}")
    assert get_response.status_code == 404

def test_update_transaction(test_client):
    # First add payment methods
    # The controller should return the new payment dict, which the router translates to a 200 response
    payment_response_1 = test_client.post("/payment/cash", params={"active": True}, json=cash_payment) 
    assert payment_response_1.status_code == 200
    payment_id_1 = payment_response_1.json()["id"]

    transaction_payload_1 = {
        "payment_method_id": payment_id_1,
        "order_id": 10,
        "amount": 25.50
    }

    # The controller should return the new transaction dict, which the router translates to a 200 response
    response_1 = test_client.post("/transaction/", json=transaction_payload_1)
    assert response_1.status_code == 200
    data_1 = response_1.json()

    data_1['amount'] = 30.50

    result = test_client.transaction_repo.update_transaction(data_1['id'], data_1)

    # Now try to retrieve transaction
    get_response = test_client.get(f"/transaction/{data_1['id']}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["payment_method_id"] == data_1["payment_method_id"]
    assert data["order_id"] == data_1["order_id"]
    assert data["amount"] == data_1["amount"]

