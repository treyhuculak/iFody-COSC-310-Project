import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.order import get_controller
from src.backend.repositories.order_repo import OrderRepository
from src.backend.controllers.order_controller import OrderController
from src.backend.models.order import OrderStatus


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

new_order_2 = {
    "id": 2,
    "timestamp": "2026-03-03T00:00:00",
    "customer_id": 1,
    "restaurant_id": 2,
    "status": "preparing",
    "total_price": 10,
    "tax": 1,
    "order_items": [
        {"item_id": 101, "quantity": 2, "order_id": 1, "subtotal": 6}
    ]
}

new_order_3 = {
    "id": 3,
    "timestamp": "2026-03-03T00:00:00",
    "customer_id": 1,
    "restaurant_id": 2,
    "status": "out for delivery",
    "total_price": 10,
    "tax": 1,
    "order_items": [
        {"item_id": 101, "quantity": 2, "order_id": 1, "subtotal": 6}
    ]
}

def test_add_order(test_client):
    # The controller should return the new restaurant dict, which the router translates to a 200 response
    response = test_client.post("/order/", json=new_order)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == 1
    assert len(data["order_items"]) == 1
    assert data["order_items"][0]["item_id"] == 101

def test_delete_order(test_client):
    response = test_client.post("/order/", json=new_order)
    response2 = test_client.post("/order/", json=new_order_2)
    response3 = test_client.post("/order/", json=new_order_3)

    assert response.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    order_id = response.json()["id"]
    order_id_2 = response2.json()["id"]
    order_id_3 = response3.json()["id"]

    # Delete order
    delete_response = test_client.delete(f"/order/{order_id}")
    assert delete_response.status_code == 200

    # Try to delete order when order status = preparing
    delete_response_2 = test_client.delete(f"/order/{order_id_2}")
    assert delete_response_2.status_code == 200

    # Try to delete order when order status = out for delivery
    delete_response_3 = test_client.delete(f"/order/{order_id_3}")
    assert delete_response_3.status_code == 403

    # After deletion, trying to get the order should return a 404
    get_response = test_client.get(f"/order/{order_id}")
    assert get_response.status_code == 404
    get_response_2 = test_client.get(f"/order/{order_id_2}")
    assert get_response_2.status_code == 404

    '''
    Order item tests:
    '''

menu_item = {
        "name": "Test Menu Item",
        "description": "A menu item for testing",
        "price": 9.99,
        "id": 0
    }

def test_get_order_items_by_order_id(test_client):
    # First add an order and an order item to ensure there is something to retrieve
    response = test_client.post("/order/", json=new_order_2)
    assert response.status_code == 200
    order_id = response.json()["id"]

    # Now try to retrieve order items for that order
    get_response = test_client.get(f"/order/{order_id}/items")
    assert get_response.status_code == 200
    data = get_response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["item_id"] == 101

def test_add_order_item_to_order(test_client):
    # First add an order to ensure there is something to add an order item to
    response = test_client.post("/order/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    # Now try to add an order item to that order
    add_response = test_client.post(f"/order/{order_id}/items", json=menu_item)
    assert add_response.status_code == 200
    data = add_response.json()
    assert data["item_id"] == menu_item["id"]
    assert data["quantity"] == 1
    assert data["subtotal"] == 9.99

def test_delete_order_item_from_order(test_client):
    # First add an order and an order item to ensure there is something to delete
    response = test_client.post("/order/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    add_response = test_client.post(f"/order/{order_id}/items", json=menu_item)
    assert add_response.status_code == 200
    item_id = add_response.json()["item_id"]

    # Now try to delete that order item
    delete_response = test_client.delete(f"/order/{order_id}/items/{item_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the order item should return a 404
    get_response = test_client.get(f"/order/{order_id}/items/{item_id}")
    assert get_response.status_code == 404

def test_update_order_item_from_order(test_client):
    # First add an order and an order item to ensure there is something to update
    response = test_client.post("/order/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    add_response = test_client.post(f"/order/{order_id}/items", json=menu_item)
    assert add_response.status_code == 200
    item_id = add_response.json()["item_id"]

    data = add_response.json()
    assert data["item_id"] == menu_item["id"]
    assert data["quantity"] == 1

    # Now try to update that order item (increment one item already existent in that order)
    add_response_2 = test_client.post(f"/order/{order_id}/items", json=menu_item)
    assert add_response_2.status_code == 200
    data_2 = add_response_2.json()
    assert data_2["item_id"] == menu_item["id"]
    assert data_2["quantity"] == 2

    # Now try to delete that order item
    delete_response = test_client.delete(f"/order/{order_id}/items/{item_id}")
    assert delete_response.status_code == 200

    deleted_data = delete_response.json()
    assert deleted_data["item_id"] == menu_item["id"]
    assert deleted_data["quantity"] == 1

def test_update_order_item_from_order_out_for_delivery(test_client):
    # First add an order and an order item to ensure there is something to update
    response = test_client.post("/order/", json=new_order_3)
    assert response.status_code == 200

    order_id_3 = response.json()["id"]

    # Try to delete order when order status = out for delivery
    delete_response_3 = test_client.delete(f"/order/{order_id_3}")
    assert delete_response_3.status_code == 403
