import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.orders import get_controller
from src.backend.repositories.order_repo import OrderRepository
from src.backend.controllers.order_controller import OrderController
from src.backend.models.order import OrderStatus, OrderLocation


new_order = {
    "customer_id": 1,
    "restaurant_id": 2, 
    "status": OrderStatus.PENDING.value,
    "location": OrderLocation.BRITISH_COLUMBIA.value,
    "order_items": [
        {"item_id": 101, "quantity": 2, "name": "Burger", "description": "A delicious burger", "price": 10.0}
    ]
}

def test_add_order(test_client):
    # The controller should return the new restaurant dict, which the router translates to a 200 response
    response = test_client.post("/orders/", json=new_order) 
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == 1
    assert len(data["order_items"]) == 1
    assert data["order_items"][0]["item_id"] == 101

def test_delete_order(test_client):
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    # Delete order
    delete_response = test_client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the order should return a 404
    get_response = test_client.get(f"/orders/{order_id}")
    assert get_response.status_code == 404