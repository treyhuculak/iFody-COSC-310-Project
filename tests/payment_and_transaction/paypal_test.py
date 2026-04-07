import json
from fastapi.testclient import TestClient
import pytest

from src.backend.main import app
from src.backend.routers.payments import get_controller as get_payment_controller
from src.backend.routers.transactions import (get_controller as get_transaction_controller, get_paypal_controller)
from src.backend.models.payment import PaymentOptions
from src.backend.repositories.transaction_repo import TransactionRepository
from src.backend.repositories.payment_repo import PaymentRepository
from src.backend.controllers.transaction_controller import TransactionController
from src.backend.controllers.payment_controller import PaymentController
from src.backend.controllers.paypal_controller import PayPalController
from src.backend.repositories.notification_repo import NotificationRepository
from src.backend.controllers.notification_controller import NotificationController


@pytest.fixture
def test_client(tmp_path):
    temp_payment_db = tmp_path / "test_payment.json"
    temp_transaction_db = tmp_path / "test_transaction.json"
    temp_notif_db = tmp_path / "test_notifications.json"
    
    temp_notif_db.write_text(json.dumps([]))
    temp_payment_db.write_text(json.dumps([]))
    temp_transaction_db.write_text(json.dumps([]))

    payment_repo = PaymentRepository(file_path=str(temp_payment_db))
    transaction_repo = TransactionRepository(file_path=str(temp_transaction_db))
    test_notif_repo = NotificationRepository(file_path=str(temp_notif_db))

    payment_controller = PaymentController(repo=payment_repo)
    notification_controller = NotificationController(repo=test_notif_repo)
    transaction_controller = TransactionController(payment_repo=payment_repo, repo=transaction_repo, notif_controller=notification_controller)
    
    paypal_controller = PayPalController(payment_repo=payment_repo, repo=transaction_repo, notif_controller=notification_controller)

    app.dependency_overrides[get_payment_controller] = lambda: payment_controller
    app.dependency_overrides[get_transaction_controller] = lambda: transaction_controller
    app.dependency_overrides[get_paypal_controller] = lambda: paypal_controller

    with TestClient(app) as client:
        client.payment_repo = payment_repo
        client.transaction_repo = transaction_repo
        yield client

    app.dependency_overrides.clear()

'''
This test touches the real paypal sandbox. I only created this test to make sure the full integration + API communication would work (our system + paypal API) 
Do not test this without having access to the sandbox (you will need access to login as a mock personal account created by the sandbox itself)
Moreover, it should be noted that we need to watch out for the personal account funds (we can edit this in the sandbox), since without enough funds, the test will not go through

def test_full_live_paypal_flow_manual_approval(test_client):
    payment_response = test_client.post("/payment/paypal", params={"active": True}, json={"user_id": 1, "method": PaymentOptions.PAYPAL.value})
    assert payment_response.status_code == 200
    payment = payment_response.json()

    paypal_payload = {
            "payment_method_id": payment["id"],
            "order_id": 1001,
            "amount": 15.75
        }

    start_response = test_client.post("/transaction/paypal/start", json=paypal_payload)
    assert start_response.status_code == 200
    paypal_started = start_response.json()

    print("\nOPEN THIS URL IN YOUR BROWSER")
    print(paypal_started["approve_url"] + "\n")

    input("After approving the payment in the PayPal sandbox browser page, press Enter here to continue: ")

    capture_response = test_client.post(f"/transaction/paypal/capture/{paypal_started['id']}")
    assert capture_response.status_code == 200
    paypal_captured = capture_response.json()

    assert paypal_captured["id"] == paypal_started["id"]
    assert paypal_captured["is_successful"] is True
    assert paypal_captured["provider_status"] == "COMPLETED"

    paypal_transaction = test_client.transaction_repo.get_transaction_by_id(paypal_started["id"])
    assert paypal_transaction is not None
    assert paypal_transaction["is_successful"] is True
    assert paypal_transaction["provider_status"] == "COMPLETED"
'''