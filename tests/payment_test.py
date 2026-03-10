import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.payment import get_controller
from src.backend.models.payment import PaymentOptions



cash_payment = {
    "user_id": 1,
    "order_id": 10,
    "amount": 25.50,
    "method": PaymentOptions.CASH.value
}

card_payment = {
    "user_id": 2,
    "order_id": 15,
    "amount": 49.99,
    "method": PaymentOptions.CREDIT_CARD.value,
    "card_digits": "1234567812345678",
    "expiration_month": 12,
    "expiration_year": 2028,
    "CVV": "123",
    "name_on_card": "Umberto De Luca"
}

def test_add_cash_payment(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/cash", json=cash_payment) 
    assert response.status_code == 200
    data = response.json()

    assert data["method"] == PaymentOptions.CASH.value
    assert data["user_id"] == 1
    assert data["order_id"] == 10
    assert data["amount"] == 25.50
    assert data["is_successful"] == True
    assert "id" in data

def test_add_card_payment(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/card", json=card_payment) 
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200
    data = response.json()

    assert data["method"] == PaymentOptions.CREDIT_CARD.value
    assert data["user_id"] == 2
    assert data["order_id"] == 15
    assert data["amount"] == 49.99
    assert data["is_successful"] == True
    assert "id" in data
    assert data["last4"] == "5678"
    #assert "CVV" not in data