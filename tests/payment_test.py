import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.payment import get_controller
from src.backend.models.payment import PaymentOptions
from src.backend.models.card_payment import CardPaymentBrand

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
    "card_digits": "4234567812345678",
    "expiration_month": 12,
    "expiration_year": 2028,
    "CVV": "123",
    "name_on_card": "Umberto De Luca"
}

card_payment_no_brand = {
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

card_expired = {
  "user_id": 2,
  "order_id": 15,
  "amount": 49.99,
  "method": "credit_card",
  "card_digits": "5234567812345678",
  "expiration_month": 5,
  "expiration_year": 2020,
  "CVV": "123",
  "name_on_card": "Test User"
}

card_invalid_CVV = {
  "user_id": 2,
  "order_id": 15,
  "amount": 49.99,
  "method": "credit_card",
  "card_digits": "1234567812345678",
  "expiration_month": 12,
  "expiration_year": 2028,
  "CVV": "12",
  "name_on_card": "Test User"
}

card_with_invalid_digits = {
  "user_id": 2,
  "order_id": 15,
  "amount": 49.99,
  "method": "credit_card",
  "card_digits": "12345678",
  "expiration_month": 12,
  "expiration_year": 2028,
  "CVV": "123",
  "name_on_card": "Test User"
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

def test_add_card_payment_with_brand(test_client):
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
    assert "CVV" not in data
    assert data["card_brand"] == CardPaymentBrand.VISA.value

def test_add_card_payment_without_brand(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/card", json=card_payment_no_brand) 
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200
    data = response.json()

    assert data["method"] == PaymentOptions.CREDIT_CARD.value
    assert data["user_id"] == 2
    assert data["order_id"] == 15
    assert data["amount"] == 49.99
    assert data["is_successful"] == False
    assert "id" in data
    assert data["last4"] == "5678"
    assert "CVV" not in data
    assert data["card_brand"] == CardPaymentBrand.NO_BRAND.value

def test_add_card_invalid_expiration_date_payment(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/card", json=card_expired) 
    print(response.status_code)
    print(response.json())
    assert response.status_code == 400

def test_add_card_invalid_CVV_payment(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/card", json=card_invalid_CVV) 
    print(response.status_code)
    print(response.json())
    assert response.status_code == 400

def test_add_card_invalid_CVV_payment(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/card", json=card_with_invalid_digits) 
    print(response.status_code)
    print(response.json())
    assert response.status_code == 400

def test_get_cash_payment_by_id(test_client):
    # First add a payment method
    response = test_client.post("/payment/cash/", json=cash_payment)
    assert response.status_code == 200
    payment_id = response.json()["id"]

    # Now try to retrieve payment
    get_response = test_client.get(f"/payment/cash/{payment_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["method"] == PaymentOptions.CASH.value
    assert data["user_id"] == 1
    assert data["order_id"] == 10
    assert data["amount"] == 25.50
    assert data["is_successful"] == True
    assert "id" in data

def test_get_card_payment_by_id(test_client):
    # First add a payment method
    response = test_client.post("/payment/card/", json=card_payment)
    assert response.status_code == 200
    payment_id = response.json()["id"]

    # Now try to retrieve payment
    get_response = test_client.get(f"/payment/card/{payment_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["method"] == PaymentOptions.CREDIT_CARD.value
    assert data["user_id"] == 2
    assert data["order_id"] == 15
    assert data["amount"] == 49.99
    assert data["is_successful"] == True
    assert "id" in data
    assert data["last4"] == "5678"
    assert "CVV" not in data
    assert data["card_brand"] == CardPaymentBrand.VISA.value

def test_delete_cash_payment(test_client):
    response = test_client.post("/payment/cash/", json=cash_payment)
    assert response.status_code == 200

    payment_id = response.json()["id"]

    # Delete payment method
    delete_response = test_client.delete(f"/payment/cash/{payment_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the payment method should return a 404
    get_response = test_client.get(f"/payment/cash/{payment_id}")
    assert get_response.status_code == 404

def test_delete_card_payment(test_client):
    response = test_client.post("/payment/card/", json=card_payment)
    assert response.status_code == 200

    payment_id = response.json()["id"]

    # Delete payment method
    delete_response = test_client.delete(f"/payment/card/{payment_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the payment method should return a 404
    get_response = test_client.get(f"/payment/card/{payment_id}")
    assert get_response.status_code == 404