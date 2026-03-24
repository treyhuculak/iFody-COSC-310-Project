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

def test_owner_can_add_order(test_client):
    # The controller should return the new order dict, which the router translates to a 200 response
    response = test_client.post("/orders/", json=new_order) 
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == 1
    assert len(data["order_items"]) == 1
    assert data["order_items"][0]["item_id"] == 101

def test_owner_can_delete_order(test_client):
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200

    order_id = response.json()["id"]

    # Delete order
    delete_response = test_client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the order should return a 404
    get_response = test_client.get(f"/orders/{order_id}")
    assert get_response.status_code == 404

def test_non_owner_cannot_delete_order(test_client):
    response = test_client.post("/orders/", json=new_order) # Customer with id 1 creates an order
    assert response.status_code == 200

    order_id = response.json()["id"] # Get the id of the newly created order

    # Try to delete order with a different customer (user 3 is a different customer, not the owner of the order)
    delete_response = test_client.delete(f"/orders/{order_id}", headers={"X-User-Id": "3"})
    assert delete_response.status_code == 403

    # The order should still exist
    get_response = test_client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200

menu_item = {
        "name": "Test Menu Item",
        "description": "A menu item for testing",
        "price": 9.99,
        "id": 0
    }

def test_owner_can_add_order_item_to_order(test_client):
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

def test_non_owner_cannot_add_order_item_to_order(test_client):
    # First add an order to ensure there is something to add an order item to
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    # Now try to add an order item to that order with a different customer (not the owner)
    add_response = test_client.post(f"/orders/{order_id}/items", params={"quantity": 2}, json=menu_item, headers={"X-User-Id": "3"})
    assert add_response.status_code == 403

    # Fetch updated order
    get_response = test_client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200

    order_data = get_response.json()

    # The order item should not have been added
    assert len(order_data["order_items"]) == 1
    assert order_data["order_items"][0]["item_id"] == 101
    assert order_data["order_items"][0]["quantity"] == 2
    assert order_data["order_items"][0]["price_at_purchase"] == 5

def test_owner_can_delete_order_item_from_order(test_client):
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

def test_non_owner_cannot_delete_order_item_from_order(test_client):
    # First add an order and an order item to ensure there is something to delete
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    add_response = test_client.post(f"/orders/{order_id}/items", params={"quantity": 1}, json=menu_item)
    assert add_response.status_code == 200
    item_id = add_response.json()["item_id"]

    # Now try to delete that order item with a different customer (not the owner)
    delete_response = test_client.delete(f"/orders/{order_id}/items/{item_id}", headers={"X-User-Id": "3"}) 
    assert delete_response.status_code == 403

    order_data = response.json()
    # Order item should still exist
    assert len(order_data["order_items"]) == 1
    assert order_data["order_items"][0]["item_id"] == 101 # The item_id should still be the same
    assert order_data["order_items"][0]["quantity"] == 2
    assert order_data["order_items"][0]["price_at_purchase"] == 5

new_restaurant = {
    "name": "Test Restaurant",
    "cuisine": "Test Cuisine",
    "location": "Kelowna",
    "delivery_fee": 5.0,
}

new_menu_item = {
    "name": "Test Pizza",
    "description": "A delicious test pizza",
    "price": 10.0,
    "id": 1
}

def test_owner_can_delete_restaurant(test_client):
    # First add a restaurant with user id 2 as owner
    response = test_client.post("/restaurants/", json=new_restaurant, headers={"X-User-Id": "2"})
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Delete the restaurant as the owner
    delete_response = test_client.delete(f"/restaurants/{restaurant_id}", headers={"X-User-Id": "2"})
    assert delete_response.status_code == 200

    # After deletion, trying to get the restaurant should return a 404
    get_response = test_client.get(f"/restaurants/{restaurant_id}", headers={"X-User-Id": "2"})
    assert get_response.status_code == 404

def test_non_owner_cannot_delete_restaurant(test_client):
    # First add a restaurant with user id 2 as owner
    response = test_client.post("/restaurants/", json=new_restaurant, headers={"X-User-Id": "2"})
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Delete the restaurant as the non owner
    delete_response = test_client.delete(f"/restaurants/{restaurant_id}", headers={"X-User-Id": "4"})
    assert delete_response.status_code == 403
    # After deletion attempt, restaurant should still exist
    get_response = test_client.get(f"/restaurants/{restaurant_id}", headers={"X-User-Id": "2"})
    assert get_response.status_code == 200

def test_owner_can_add_menu_item_to_restaurant(test_client):
    # First add a restaurant with user id 2 as owner
    response = test_client.post("/restaurants/", json=new_restaurant, headers={"X-User-Id": "2"})
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Now try to add a menu item as user id 2 (the owner)
    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=new_menu_item, headers={"X-User-Id": "2"})

    assert add_response.status_code == 200
    data = add_response.json()

    assert data["name"] == new_menu_item["name"]
    assert data["description"] == new_menu_item["description"]
    assert data["price"] == new_menu_item["price"]

def test_non_owner_cannot_add_menu_item_to_restaurant(test_client):
    # First add a restaurant with user id 2 as owner
    response = test_client.post("/restaurants/", json=new_restaurant, headers={"X-User-Id": "2"})
    
    assert response.status_code == 200
    restaurant_id = response.json()["id"]
    
    # Now try to add a menu item as user id 4 (not the owner)
    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=new_menu_item, headers={"X-User-Id": "4"})
    
    assert add_response.status_code == 403  # Forbidden - non-owner trying to add menu item

    get_reponse = test_client.get(f"/restaurants/{restaurant_id}/menu")
    data = get_reponse.json()

    assert get_reponse.status_code == 200
    assert data["items"] == []  # Menu should still be empty since the add was forbidden

def test_owner_can_delete_menu_item_from_restaurant(test_client):
    # First add a restaurant and a menu item as user id 2 (the owner)
    response = test_client.post("/restaurants/", json=new_restaurant, headers={"X-User-Id": "2"})
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=new_menu_item, headers={"X-User-Id": "2"})
    assert add_response.status_code == 200
    menu_item_id = add_response.json()["id"]

    # Now try to delete that menu item as the owner
    delete_response = test_client.delete(f"/restaurants/{restaurant_id}/menu/{menu_item_id}", headers={"X-User-Id": "2"})
    assert delete_response.status_code == 200

    # After deletion, trying to get the menu item should return a 404
    get_response = test_client.get(f"/restaurants/{restaurant_id}/menu/{menu_item_id}", headers={"X-User-Id": "2"})
    assert get_response.status_code == 404

def test_non_owner_cannot_delete_menu_item_from_restaurant(test_client):
    # First add a restaurant and a menu item as user id 2 (the owner)
    response = test_client.post("/restaurants/", json=new_restaurant, headers={"X-User-Id": "2"})
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=new_menu_item, headers={"X-User-Id": "2"})
    assert add_response.status_code == 200
    menu_item_id = add_response.json()["id"]

    # Now try to delete that menu item as the non owner
    delete_response = test_client.delete(f"/restaurants/{restaurant_id}/menu/{menu_item_id}", headers={"X-User-Id": "4"})
    assert delete_response.status_code == 403

    # After deletion, trying to get the menu item should be the same
    get_response = test_client.get(f"/restaurants/{restaurant_id}/menu", headers={"X-User-Id": "2"})
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["items"][0]["id"] == menu_item_id