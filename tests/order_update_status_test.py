import pytest
from src.backend.models.order import OrderCreate, OrderStatus, OrderLocation
from src.backend.models.order_item import OrderItem

new_order = OrderCreate(
    customer_id=1,
    restaurant_id=2,
    status=OrderStatus.PENDING,
    location=OrderLocation.BRITISH_COLUMBIA,
    order_items=[
        OrderItem(item_id=101, quantity=2, price_at_purchase=5.0)
    ]
)

def test_mgr_update_order(test_client):
    order_data = new_order.model_dump()
    # Serialize enums to their values for JSON
    order_data['status'] = order_data['status'].value
    order_data['location'] = order_data['location'].value
    response = test_client.post("/orders/", json=order_data)
    order_id = response.json()["id"]

    response = test_client.put(f"/orders/{order_id}/status?new_status=preparing&role=manager")
    assert response.status_code == 200

def test_cstm_update_order(test_client):
    response = test_client.put("/orders/1/status?new_status=preparing&role=customer")
    assert response.status_code == 403

def test_invalid_order(test_client):
    response = test_client.put("/orders/0/status?new_status=preparing&role=manager")
    assert response.status_code == 404