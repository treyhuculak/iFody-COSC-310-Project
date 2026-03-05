import pytest

new_order = {
    "id": 1,
    "timestamp": "2026-03-03T00:00:00",
    "customer_id": 1,
    "restaurant_id": 2,
    "status": "pending",
    "total_price": 10,
    "tax": 1,
    "order_items": [
        {"item_id": 101, "quantity": 2, "order_id": 1, "subtotal": 6}
    ]
}

def test_mgr_update_order(test_client):
    response = test_client.post("/order/", json=new_order)
    order_id = response.json()["id"]

    response = test_client.put(f"/order/{order_id}/status?new_status=preparing&role=manager")
    assert response.status_code == 200

def test_cstm_update_order(test_client):
    response = test_client.put("/order/1/status?new_status=preparing&role=customer")
    assert response.status_code == 403

def test_invalid_order(test_client):
    response = test_client.put("/order/0/status?new_status=preparing&role=manager")
    assert response.status_code == 404