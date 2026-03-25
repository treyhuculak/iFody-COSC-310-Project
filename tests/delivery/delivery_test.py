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
from src.backend.models.order import OrderLocation, OrderStatus
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


    sample_order = {
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
    }

    sample_delivery = {
        "id": 1,
        "order_id": 1,
        "driver_id": 1,
        "assigned_at": datetime.now().isoformat(),
        "estimated_delivery_time": (datetime.now() + timedelta(minutes = 30)).isoformat(),
    }
    
    temp_order_db.write_text(json.dumps([sample_order]))
    temp_delivery_db.write_text(json.dumps([sample_delivery]))

    order_repo = OrderRepository(file_path=str(temp_order_db))
    delivery_repo = DeliveryRepository(file_path=str(temp_delivery_db))

    delivery_controller = DeliveryController(repo=delivery_repo, order_repo=order_repo)

    order_controller = OrderController(repo=order_repo, delivery_controller=delivery_controller)

    app.dependency_overrides[get_order_controller] = lambda: order_controller
    app.dependency_overrides[get_delivery_controller] = lambda: delivery_controller

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

test_delivery_service = DeliveryService()

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

def test_delete_delivery_with_invalid_id(test_client):
    delivery_id = 999

    # Delete delivery should give 404 since no delivery exists with that delivery id
    delete_response = test_client.delete(f"/deliveries/{delivery_id}")
    assert delete_response.status_code == 404

def test_delete_delivery(test_client):
    delivery_id = 1

    # Delete delivery
    delete_response = test_client.delete(f"/deliveries/{delivery_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the delivery should return a 404
    get_response = test_client.get(f"/deliveries/{delivery_id}")
    assert get_response.status_code == 404

def test_assign_delivered_at_time(test_client):
    delivery_id = 1
    time = datetime.now().isoformat()

    # Assign a delivered_at time
    update_response = test_client.put(f"/deliveries/{delivery_id}/{time}")
    assert update_response.status_code == 200

    # Now try to retrieve the updated delivery
    get_response = test_client.get(f"/deliveries/{delivery_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["delivered_at"] == time

def test_get_delivery_by_order_id(test_client):
    order_id = 1
    # Should return 200
    get_response = test_client.get(f"/deliveries/order/{order_id}")
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["id"] == 1
    assert data["order_id"] == 1
    assert data["driver_id"] == 1

def test_get_delivery_by_invalid_order_id(test_client):
    order_id = 999
    # Should return 404
    get_response = test_client.get(f"/deliveries/order/{order_id}")
    assert get_response.status_code == 404

def test_calculate_estimated_delivery_time_bc():
    # This way we ensure a correct behavior even if a few ms has passed in between the calls
    before = datetime.now()
    result = test_delivery_service.calculate_estimated_delivery_time(OrderLocation.BRITISH_COLUMBIA.value)
    after = datetime.now()

    result_dt = datetime.fromisoformat(result)

    assert before + timedelta(minutes=30) <= result_dt <= after + timedelta(minutes=30)

def test_calculate_estimated_delivery_time_other_location():
    # This way we ensure a correct behavior even if a few ms has passed in between the calls
    before = datetime.now()
    result = test_delivery_service.calculate_estimated_delivery_time(OrderLocation.ALBERTA.value)
    after = datetime.now()

    result_dt = datetime.fromisoformat(result)

    assert before + timedelta(minutes=120) <= result_dt <= after + timedelta(minutes=120)

def test_assign_delivery_driver_assigns_driver_when_under_60_minutes():
    delivery_data = {
        "estimated_delivery_time": (datetime.now() + timedelta(minutes=30)).isoformat()
    }

    result = test_delivery_service.assign_delivery_driver(delivery_data)

    assert result is True
    assert delivery_data["driver_id"] == 1
    assert "assigned_at" in delivery_data

def test_assign_delivery_driver_does_not_assign_when_over_60_minutes():
    delivery_data = {
        "estimated_delivery_time": (datetime.now() + timedelta(minutes=90)).isoformat()
    }

    result = test_delivery_service.assign_delivery_driver(delivery_data)

    assert result is False
    assert "driver_id" not in delivery_data
    assert "assigned_at" not in delivery_data

'''
Integration test with order
'''
def test_order_to_delivery_integration(test_client):
    order_payload = {
        "customer_id": 1,
        "restaurant_id": 2,
        "status": OrderStatus.PREPARING_ORDER.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": []
    }

    create_order_response = test_client.post("/orders/", json=order_payload, headers={"X-User-Id": "1"})
    assert create_order_response.status_code == 200

    order_id = create_order_response.json()["id"]

    # Updating order status and creating delivery
    update_response = test_client.put(f"/orders/{order_id}/status", params={"new_status": OrderStatus.OUT_FOR_DELIVERY.value, "role": "manager"})
    assert update_response.status_code == 200

    # Ensuring the delivery is there
    delivery_response = test_client.get(f"/deliveries/order/{order_id}")
    assert delivery_response.status_code == 200

    delivery_data = delivery_response.json()
    assert delivery_data["order_id"] == order_id
    assert delivery_data["driver_id"] == 1
    assert delivery_data["assigned_at"] is not None
    assert delivery_data["estimated_delivery_time"] is not None
    assert delivery_data["delivered_at"] is None

    # Updating order so arrive_at variable from delivery is assigned a value
    delivered_response = test_client.put(f"/orders/{order_id}/status", params={"new_status": OrderStatus.DELIVERED.value, "role": "manager"})
    assert delivered_response.status_code == 200

    # Getting the updated delivery and ensuring arrived_at is there
    updated_delivery_response = test_client.get(f"/deliveries/order/{order_id}")
    assert updated_delivery_response.status_code == 200

    updated_delivery = updated_delivery_response.json()
    assert updated_delivery["delivered_at"] is not None
    