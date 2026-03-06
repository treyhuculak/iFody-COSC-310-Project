import pytest
from src.backend.models.order import OrderCreate, OrderStatus, OrderLocation

new_order = {
    "customer_id": 1,
    "restaurant_id": 2,
    "status": OrderStatus.PENDING.value,
    "location": OrderLocation.BRITISH_COLUMBIA.value,
    "order_items": [
        {"item_id": 101, "quantity": 2, "name": "Burger", "description": "A delicious burger", "price": 10.0}
    ]
}

def test_mgr_update_order(test_client):
    response = test_client.post("/orders/", json=new_order)
    order_id = response.json()["id"]

    response = test_client.put(f"/orders/{order_id}/status?new_status=preparing&role=manager")
    assert response.status_code == 200

def test_cstm_update_order(test_client):
    response = test_client.put("/orders/1/status?new_status=preparing&role=customer")
    assert response.status_code == 403

def test_invalid_order(test_client):
    response = test_client.put("/orders/0/status?new_status=preparing&role=manager")
    assert response.status_code == 404