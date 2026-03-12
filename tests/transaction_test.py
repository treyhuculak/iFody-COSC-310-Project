import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.payment import get_controller as get_payment_controller
from src.backend.routers.transaction import get_controller as get_transaction_controller
from src.backend.models.payment import PaymentOptions
from src.backend.repositories.transaction_repo import TransactionRepository
from src.backend.repositories.payment_repo import PaymentRepository
from src.backend.controllers.transaction_controller import TransactionController
from src.backend.controllers.payment_controller import PaymentController

@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real
    data/transaction.json & data/payment.json.  The temp file is deleted automatically after each
    test, so the production database is never touched.
    """
    temp_payment_db = tmp_path / "test_payment.json"
    temp_transaction_db = tmp_path / "test_transaction.json"

    temp_payment_db.write_text(json.dumps([]))
    temp_transaction_db.write_text(json.dumps([]))

    shared_payment_repo = PaymentRepository(file_path=str(temp_payment_db))
    transaction_repo = TransactionRepository(file_path=str(temp_transaction_db))

    payment_controller = PaymentController(repo=shared_payment_repo)
    transaction_controller = TransactionController(payment_repo=shared_payment_repo, repo=transaction_repo)

    app.dependency_overrides[get_payment_controller] = lambda: payment_controller
    app.dependency_overrides[get_transaction_controller] = lambda: transaction_controller

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

cash_payment = {
    "user_id": 1,
    "method": PaymentOptions.CASH.value
}

card_payment = {
    "user_id": 2,
    "method": PaymentOptions.CREDIT_CARD.value,
    "card_digits": "4234567812345678",
    "expiration_month": 12,
    "expiration_year": 2028,
    "CVV": "123",
    "name_on_card": "Umberto De Luca"
}

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
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200

    data = response.json()
    assert data["payment_method_id"] == payment_id
    assert data["order_id"] == 15
    assert data["amount"] == 45.50
    assert data["is_successful"] is True
    assert "id" in data

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
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200

    data = response.json()
    assert data["payment_method_id"] == payment_id
    assert data["order_id"] == 10
    assert data["amount"] == 25.50
    assert data["is_successful"] is True
    assert "id" in data