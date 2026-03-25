import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.payments import get_controller
from src.backend.models.payment import PaymentOptions
from src.backend.models.card_payment import CardPaymentBrand
from src.backend.repositories.payment_repo import PaymentRepository
from src.backend.controllers.payment_controller import PaymentController

@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real
    data/payment.json.  The temp file is deleted automatically after each
    test, so the production database is never touched.
    """
    temp_db = tmp_path / "test_payment.json"
    temp_db.write_text(json.dumps([]))

    test_repo = PaymentRepository(file_path=str(temp_db))
    test_controller = PaymentController(repo=test_repo)

    app.dependency_overrides[get_controller] = lambda: test_controller

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

cash_payment = {
    "user_id": 2,
    "method": PaymentOptions.CASH.value
}

invalid_cash_payment = {
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

invalid_card_payment = {
    "user_id": 2,
    "method": PaymentOptions.CREDIT_CARD.value,
    "card_digits": "4234567812345678"
}

card_payment_2 = {
    "user_id": 1,
    "method": PaymentOptions.CREDIT_CARD.value,
    "card_digits": "4234567812345678",
    "expiration_month": 12,
    "expiration_year": 2028,
    "CVV": "123",
    "name_on_card": "Umberto De Luca"
}

card_payment_no_brand = {
    "user_id": 2,
    "method": PaymentOptions.CREDIT_CARD.value,
    "card_digits": "1234567812345678",
    "expiration_month": 12,
    "expiration_year": 2028,
    "CVV": "123",
    "name_on_card": "Umberto De Luca"
}

card_expired = {
  "user_id": 2,
  "method": "credit_card",
  "card_digits": "5234567812345678",
  "expiration_month": 5,
  "expiration_year": 2020,
  "CVV": "123",
  "name_on_card": "Test User"
}

card_invalid_CVV = {
  "user_id": 2,
  "method": "credit_card",
  "card_digits": "1234567812345678",
  "expiration_month": 12,
  "expiration_year": 2028,
  "CVV": "12",
  "name_on_card": "Test User"
}

card_with_invalid_digits = {
  "user_id": 2,
  "method": "credit_card",
  "card_digits": "12345678",
  "expiration_month": 12,
  "expiration_year": 2028,
  "CVV": "123",
  "name_on_card": "Test User"
}

def test_add_cash_payment(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/cash", params={"active": True}, json=cash_payment) 
    assert response.status_code == 200
    data = response.json()

    assert data["method"] == PaymentOptions.CASH.value
    assert data["user_id"] == 2
    assert data["is_active"] == True
    assert "id" in data

def test_add_invalid_cash_payment(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/cash", params={"active": True}, json=invalid_cash_payment) 
    assert response.status_code == 422

def test_add_card_payment_with_brand(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/card", params={"active": True}, json=card_payment) 
    assert response.status_code == 200
    data = response.json()

    assert data["method"] == PaymentOptions.CREDIT_CARD.value
    assert data["user_id"] == 2
    assert data["is_active"] == True
    assert "id" in data
    assert data["last4"] == "5678"
    assert "CVV" not in data
    assert data["card_brand"] == CardPaymentBrand.VISA.value

def test_add_invalid_card_payment(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/card", params={"active": True}, json=invalid_card_payment) 
    assert response.status_code == 422

def test_add_card_payment_without_brand(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/card", params={"active": False}, json=card_payment_no_brand) 
    assert response.status_code == 200
    data = response.json()

    assert data["method"] == PaymentOptions.CREDIT_CARD.value
    assert data["is_active"] == False
    assert "id" in data
    assert data["last4"] == "5678"
    assert "CVV" not in data
    assert data["card_brand"] == CardPaymentBrand.NO_BRAND.value

def test_add_card_invalid_expiration_date_payment(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/card", params={"active": False}, json=card_expired) 
    assert response.status_code == 400

def test_add_card_invalid_CVV_payment(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/card", params={"active": False}, json=card_invalid_CVV) 
    assert response.status_code == 400

def test_add_card_invalid_digits_payment(test_client):
    # The controller should return the new payment dict, which the router translates to a 200 response
    response = test_client.post("/payment/card", params={"active": False}, json=card_with_invalid_digits) 
    assert response.status_code == 400

def test_get_cash_payment_by_id(test_client):
    # First add a payment method
    response = test_client.post("/payment/cash/", params={"active": True}, json=cash_payment)
    assert response.status_code == 200
    payment_id = response.json()["id"]

    # Now try to retrieve payment
    get_response = test_client.get(f"/payment/cash/{payment_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["method"] == PaymentOptions.CASH.value
    assert data["user_id"] == 2
    assert data["is_active"] == True
    assert "id" in data

def test_get_cash_payment_by_invalid_id(test_client):
    # First add a payment method
    response = test_client.post("/payment/cash/", params={"active": True}, json=cash_payment)
    assert response.status_code == 200
    payment_id = 999

    # Now try to retrieve payment
    get_response = test_client.get(f"/payment/cash/{payment_id}")
    assert get_response.status_code == 404

def test_get_card_payment_by_id(test_client):
    # First add a payment method
    response = test_client.post("/payment/card/", params={"active": True}, json=card_payment)
    assert response.status_code == 200
    payment_id = response.json()["id"]

    # Now try to retrieve payment
    get_response = test_client.get(f"/payment/card/{payment_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["method"] == PaymentOptions.CREDIT_CARD.value
    assert data["user_id"] == 2
    assert data["is_active"] == True
    assert "id" in data
    assert data["last4"] == "5678"
    assert "CVV" not in data
    assert data["card_brand"] == CardPaymentBrand.VISA.value

def test_get_card_payment_by_invalid_id(test_client):
    # First add a payment method
    response = test_client.post("/payment/card/", params={"active": True}, json=card_payment)
    assert response.status_code == 200
    payment_id = 999

    # Now try to retrieve payment should give 404 since no paymnet exists with that payment id
    get_response = test_client.get(f"/payment/card/{payment_id}")
    assert get_response.status_code == 404

def test_delete_cash_payment(test_client):
    response = test_client.post("/payment/cash/", params={"active": True}, json=cash_payment)
    assert response.status_code == 200

    payment_id = response.json()["id"]

    # Delete payment method
    delete_response = test_client.delete(f"/payment/cash/{payment_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the payment method should return a 404
    get_response = test_client.get(f"/payment/cash/{payment_id}")
    assert get_response.status_code == 404

def test_delete_cash_payment_with_invalid_id(test_client):
    response = test_client.post("/payment/cash/", params={"active": True}, json=cash_payment)
    assert response.status_code == 200

    payment_id = 999

    # Delete payment method should give 404 since no payment exists with that payment id
    delete_response = test_client.delete(f"/payment/cash/{payment_id}")
    assert delete_response.status_code == 404

def test_delete_card_payment(test_client):
    response = test_client.post("/payment/card/", params={"active": True}, json=card_payment)
    assert response.status_code == 200

    payment_id = response.json()["id"]

    # Delete payment method
    delete_response = test_client.delete(f"/payment/card/{payment_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the payment method should return a 404
    get_response = test_client.get(f"/payment/card/{payment_id}")
    assert get_response.status_code == 404

def test_delete_card_payment_with_invalid_id(test_client):
    response = test_client.post("/payment/card/", params={"active": True}, json=card_payment)
    assert response.status_code == 200

    payment_id = 999

    # Delete payment method should retrieve 404 since no payment exists with that payment id
    delete_response = test_client.delete(f"/payment/card/{payment_id}")
    assert delete_response.status_code == 404

def test_get_payment_methods_by_user_id(test_client):
    # First add payment methods
    response1 = test_client.post("/payment/cash/", params={"active": False}, json=cash_payment)
    assert response1.status_code == 200
    payment1_id = response1.json()["id"]

    response2 = test_client.post("/payment/card/", params={"active": True}, json=card_payment)
    assert response2.status_code == 200
    payment2_id = response2.json()["id"]

    response3 = test_client.post("/payment/card/", params={"active": False}, json=card_payment_no_brand)
    assert response3.status_code == 200
    payment3_id = response3.json()["id"]

    response4 = test_client.post("/payment/card/", params={"active": True}, json=card_payment_2)
    assert response4.status_code == 200
    payment4_id = response4.json()["id"]

    # All responses (not counting response 4 since it is suppose to have a different user id) suppose to have the same user_id
    user_id = response1.json()["user_id"]

    # Now try to retrieve payment methods
    get_response = test_client.get(f"/payment/{user_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data) == 3
    assert data[0]["id"] == payment1_id
    assert data[1]["id"] == payment2_id
    assert data[2]["id"] == payment3_id

    # Ensuring payment methods from different users do not appear here
    ids = [payment["id"] for payment in data]
    assert payment4_id not in ids

def test_get_payment_methods_by_invalid_user_id(test_client):
    # First add payment methods
    response1 = test_client.post("/payment/cash/", params={"active": False}, json=cash_payment)
    assert response1.status_code == 200

    response2 = test_client.post("/payment/card/", params={"active": True}, json=card_payment)
    assert response2.status_code == 200

    # All responses (not counting response 4 since it is suppose to have a different user id) suppose to have the same user_id
    user_id = 999

    # Now try to retrieve payment methods, should retrieve 404 since no user id exists with that user_id
    get_response = test_client.get(f"/payment/{user_id}")
    assert get_response.status_code == 404

def test_get_active_cash_payment_method(test_client):
    # First add payment methods
    response1 = test_client.post("/payment/cash/", params={"active": True}, json=cash_payment)
    assert response1.status_code == 200
    payment1_id = response1.json()["id"]

    response2 = test_client.post("/payment/card/", params={"active": False}, json=card_payment)
    assert response2.status_code == 200

    # All responses suppose to have the same user_id
    user_id = response1.json()["user_id"]

    # Now try to retrieve the active payment method
    get_response = test_client.get(f"/payment/active/{user_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["method"] == PaymentOptions.CASH.value
    assert data["user_id"] == 2
    assert data["is_active"] == True
    assert data["id"] == payment1_id

def test_get_active_cash_payment_method_with_no_active_method(test_client):
    # First add payment methods
    response1 = test_client.post("/payment/cash/", params={"active": False}, json=cash_payment)
    assert response1.status_code == 200

    response2 = test_client.post("/payment/card/", params={"active": False}, json=card_payment)
    assert response2.status_code == 200

    # All responses suppose to have the same user_id
    user_id = response1.json()["user_id"]

    # Now try to retrieve the active payment method
    get_response = test_client.get(f"/payment/active/{user_id}")
    assert get_response.status_code == 404

def test_get_active_card_payment_method(test_client):
    # First add payment methods
    response1 = test_client.post("/payment/cash/", params={"active": False}, json=cash_payment)
    assert response1.status_code == 200

    response2 = test_client.post("/payment/card/", params={"active": True}, json=card_payment)
    assert response2.status_code == 200
    payment2_id = response2.json()["id"]

    # All responses suppose to have the same user_id
    user_id = response1.json()["user_id"]

    # Now try to retrieve the active payment method
    get_response = test_client.get(f"/payment/active/{user_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["method"] == PaymentOptions.CREDIT_CARD.value
    assert data["user_id"] == 2
    assert data["is_active"] == True
    assert data["card_brand"] == CardPaymentBrand.VISA.value
    assert data["id"] == payment2_id

def test_get_active_card_payment_method_with_no_active_method(test_client):
    # First add payment methods
    response1 = test_client.post("/payment/cash/", params={"active": False}, json=cash_payment)
    assert response1.status_code == 200

    response2 = test_client.post("/payment/card/", params={"active": False}, json=card_payment)
    assert response2.status_code == 200

    # All responses suppose to have the same user_id
    user_id = response1.json()["user_id"]

    # Now try to retrieve the active payment method
    get_response = test_client.get(f"/payment/active/{user_id}")
    assert get_response.status_code == 404

def test_switch_active_payment_method(test_client):
    # First add payment methods
    response1 = test_client.post("/payment/cash/", params={"active": True}, json=cash_payment)
    assert response1.status_code == 200
    payment1_id = response1.json()["id"]

    response2 = test_client.post("/payment/card/", params={"active": False}, json=card_payment)
    assert response2.status_code == 200
    payment2_id = response2.json()["id"]

    # All responses suppose to have the same user_id
    user_id = response1.json()["user_id"]

    # Switch active payment method
    update_response = test_client.put(f"/payment/active/{user_id}/{payment2_id}")
    assert update_response.status_code == 200

    # Now try to retrieve the active payment method
    get_response = test_client.get(f"/payment/active/{user_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["method"] == PaymentOptions.CREDIT_CARD.value
    assert data["user_id"] == 2
    assert data["is_active"] == True
    assert data["id"] == payment2_id

    # Now try to retrieve the other payment method (not active anymore)
    get_response = test_client.get(f"/payment/cash/{payment1_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["method"] == PaymentOptions.CASH.value
    assert data["user_id"] == 2
    assert data["is_active"] == False
    

