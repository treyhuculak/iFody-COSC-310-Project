import json
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from src.backend.main import app
from src.backend.routers.orders import get_controller as get_order_controller
from src.backend.routers.deliveries import get_controller as get_delivery_controller
from src.backend.repositories.delivery_repo import DeliveryRepository
from src.backend.repositories.order_repo import OrderRepository
from src.backend.controllers.delivery_controller import DeliveryController
from src.backend.controllers.order_controller import OrderController
from src.backend.models.order import OrderLocation
from src.backend.services.delivery_service import DeliveryService

@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real
    data/delivery.json & data/order.json.  The temp file is deleted automatically after each
    test, so the production database is never touched.
    """
    temp_order_db = tmp_path / "test_order.json"
    temp_delivery_db = tmp_path / "test_delivery.json"

    temp_order_db.write_text(json.dumps([{
        "id": 1,
        "customer_id": 1,
        "restaurant_id": 2,
        "status": "pending",
        "location": "BC",
        "order_items": [],
        "timestamp": "2026-03-23T17:00:00",
        "subtotal_price": 10.0,
        "total_price": 12.0,
        "tax": 2.0,
        "delivery_fee": 0.0
    }]))
    temp_delivery_db.write_text(json.dumps([{
        "id": 1,
        "order_id": 1,
        "driver_id": 1,
        "assigned_at": datetime.now().isoformat(),
        "estimated_delivery_time": (datetime.now() + timedelta(minutes = 30)).isoformat(),
    }]))

    shared_order_repo = OrderRepository(file_path=str(temp_order_db))
    delivery_repo = DeliveryRepository(file_path=str(temp_delivery_db))

    order_controller = OrderController(repo=shared_order_repo)
    delivery_controller = DeliveryController(order_repo=shared_order_repo, repo=delivery_repo)

    app.dependency_overrides[get_order_controller] = lambda: order_controller
    app.dependency_overrides[get_delivery_controller] = lambda: delivery_controller

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

delivery_service = DeliveryService()

def test_get_delivery(test_client):
    delivery_id = 1
    # Should return 200
    get_response = test_client.get(f"/deliveries/{delivery_id}")
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["id"] == 1
    assert data["order_id"] == 1
    assert data["driver_id"] == 1

def test_get_delivery_with_invalid_id(test_client):
    delivery_id = 999
    # Should return 404 -> No delivery id == 999
    get_response = test_client.get(f"/deliveries/{delivery_id}")
    assert get_response.status_code == 404

def test_create_delivery_with_invalid_fields(test_client):
    delivery_payload = {}

    # Should return 422 since the delivery has not the correct fields for DeliveryCreate
    response = test_client.post("/deliveries/", json=delivery_payload)
    assert response.status_code == 422

def test_create_delivery(test_client):
    delivery_payload = {
        "order_id": 1
    }

    # Should return 200
    response = test_client.post("/deliveries/", json=delivery_payload)
    assert response.status_code == 200

def test_delete_cash_payment_with_invalid_id(test_client):
    delivery_id = 999

    # Delete delivery should give 404 since no delivery exists with that delivery id
    delete_response = test_client.delete(f"/deliveries/{delivery_id}")
    assert delete_response.status_code == 404

def test_delete_card_payment(test_client):
    delivery_id = 1

    # Delete delivery
    delete_response = test_client.delete(f"/deliveries/{delivery_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the payment method should return a 404
    get_response = test_client.get(f"/deliveries/{delivery_id}")
    assert get_response.status_code == 404

def test_assign_delivered_at_time(test_client):
    delivery_id = 1
    time = datetime.now().isoformat()

    # Assign a delivered_at time
    update_response = test_client.put(f"/deliveries/{delivery_id}/{time}")
    assert update_response.status_code == 200

    # Now try to retrieve the active payment method
    get_response = test_client.get(f"/deliveries/{delivery_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["delivered_at"] == time

def test_get_delivery_by_order_id(test_client):
    order_id = 1
    # Should return 200
    get_response = test_client.get(f"/deliveries/order_id/{order_id}")
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["id"] == 1
    assert data["order_id"] == 1
    assert data["driver_id"] == 1

def test_get_delivery_by_invalid_order_id(test_client):
    order_id = 999
    # Should return 404
    get_response = test_client.get(f"/deliveries/order_id/{order_id}")
    assert get_response.status_code == 404

def test_calculate_estimated_delivery_time_bc():
    # This way we ensure a correct behavior even if a few ms has passed in between the calls
    before = datetime.now()
    result = delivery_service.calculate_estimated_delivery_time(OrderLocation.BRITISH_COLUMBIA.value)
    after = datetime.now()

    result_dt = datetime.fromisoformat(result)

    assert before + timedelta(minutes=30) <= result_dt <= after + timedelta(minutes=30)

def test_calculate_estimated_delivery_time_other_location():
    # This way we ensure a correct behavior even if a few ms has passed in between the calls
    before = datetime.now()
    result = delivery_service.calculate_estimated_delivery_time(OrderLocation.ALBERTA.value)
    after = datetime.now()

    result_dt = datetime.fromisoformat(result)

    assert before + timedelta(minutes=120) <= result_dt <= after + timedelta(minutes=120)

def test_assign_delivery_driver_assigns_driver_when_under_60_minutes():
    delivery_data = {
        "estimated_delivery_time": (datetime.now() + timedelta(minutes=30)).isoformat()
    }

    result = delivery_service.assign_delivery_driver(delivery_data)

    assert result is True
    assert delivery_data["driver_id"] == 1
    assert "assigned_at" in delivery_data

def test_assign_delivery_driver_does_not_assign_when_over_60_minutes():
    delivery_data = {
        "estimated_delivery_time": (datetime.now() + timedelta(minutes=90)).isoformat()
    }

    result = delivery_service.assign_delivery_driver(delivery_data)

    assert result is False
    assert "driver_id" not in delivery_data
    assert "assigned_at" not in delivery_data
    