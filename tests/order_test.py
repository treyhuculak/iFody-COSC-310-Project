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
        {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
    ]
}

new_order_2 = {
    "customer_id": 1,
    "restaurant_id": 2,
    "status": OrderStatus.PREPARING_ORDER.value,
    "location": OrderLocation.BRITISH_COLUMBIA.value,
    "order_items": [
        {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
    ]
}

new_order_3 = {
    "customer_id": 1,
    "restaurant_id": 2,
    "status": OrderStatus.OUT_FOR_DELIVERY.value,
    "location": OrderLocation.BRITISH_COLUMBIA.value,
    "order_items": [
        {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
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

def test_delete_order_preparing(test_client):
    response = test_client.post("/orders/", json=new_order_2)

    assert response.status_code == 200

    order_id = response.json()["id"]

    # Try to delete order when order status = preparing
    delete_response = test_client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the order should return a 404
    get_response = test_client.get(f"/orders/{order_id}")
    assert get_response.status_code == 404    

def test_delete_order_out_for_delivery(test_client):
    response = test_client.post("/orders/", json=new_order_3)

    assert response.status_code == 200

    order_id = response.json()["id"]

    # Try to delete order when order status = out for delivery
    delete_response = test_client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 403

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
    response = test_client.post("/orders/", json=new_order_2)
    assert response.status_code == 200
    order_id = response.json()["id"]

    # Now try to retrieve order items for that order
    get_response = test_client.get(f"/orders/{order_id}/items")
    assert get_response.status_code == 200
    data = get_response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["item_id"] == 101

def test_add_order_item_to_order(test_client):
    # First add an order to ensure there is something to add an order item to
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    # Now try to add an order item to that order
    add_response = test_client.post(f"/orders/{order_id}/items", params={"quantity": 2}, json=menu_item)
    assert add_response.status_code == 200

    # Fetch updated order
    get_response = test_client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200

    order_data = get_response.json()

    assert len(order_data["order_items"]) == 2
    assert order_data["order_items"][1]["item_id"] == menu_item["id"]
    assert order_data["order_items"][1]["quantity"] == 2
    assert order_data["order_items"][1]["price_at_purchase"] == menu_item["price"]

def test_delete_order_item_from_order(test_client):
    # First add an order and an order item to ensure there is something to delete
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    add_response = test_client.post(f"/orders/{order_id}/items", params={"quantity": 1}, json=menu_item)
    assert add_response.status_code == 200
    item_id = add_response.json()["item_id"]

    # Now try to delete that order item
    delete_response = test_client.delete(f"/orders/{order_id}/items/{item_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the order item should return a 404
    get_response = test_client.get(f"/orders/{order_id}/items/{item_id}")
    assert get_response.status_code == 404

def test_update_order_item_from_order(test_client):
    # First add an order and an order item to ensure there is something to update
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    add_response = test_client.post(f"/orders/{order_id}/items", params={"quantity": 1}, json=menu_item)
    assert add_response.status_code == 200
    item_id = add_response.json()["item_id"]

    data = add_response.json()
    assert data["item_id"] == menu_item["id"]
    assert data["quantity"] == 1

    # Now try to update that order item (increment one item already existent in that order)
    add_response_2 = test_client.post(f"/orders/{order_id}/items", params={"quantity": 1}, json=menu_item)
    assert add_response_2.status_code == 200

    # Fetch updated order
    get_response = test_client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200

    order_data = get_response.json()
    assert order_data["order_items"][1]["item_id"] == menu_item["id"]
    assert order_data["order_items"][1]["quantity"] == 2

    # Now try to delete that order item
    delete_response = test_client.delete(f"/orders/{order_id}/items/{item_id}")
    assert delete_response.status_code == 200

    deleted_data = delete_response.json()
    assert deleted_data["item_id"] == menu_item["id"]
    assert deleted_data["quantity"] == 1

def test_update_order_item_from_order_out_for_delivery(test_client):
    # First add an order and an order item to ensure there is something to update
    response = test_client.post("/orders/", json=new_order_3)
    assert response.status_code == 200

    order_id_3 = response.json()["id"]

    # Try to delete order when order status = out for delivery
    delete_response_3 = test_client.delete(f"/orders/{order_id_3}")
    assert delete_response_3.status_code == 403
