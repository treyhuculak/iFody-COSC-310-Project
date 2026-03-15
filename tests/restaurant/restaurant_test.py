import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.models.pagination import PaginatedResponse
from src.backend.routers.restaurants import get_controller
from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.controllers.restaurant_controller import RestaurantController
from src.backend.repositories.user_repo import UserRepository
import src.backend.utils.auth_dependencies as auth_dependencies


@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real
    data/restaurants.json.  The temp file is deleted automatically after each
    test, so the production database is never touched.
    """
    temp_db = tmp_path / "test_restaurants.json"
    temp_db.write_text(json.dumps([]))

    temp_user_db = tmp_path / "test_users.json"
    temp_user_db.write_text(json.dumps({
        "Users": [
            {
                "id": 1,
                "username": "TestCustomer",
                "email": "testcustomer@example.com",
                "password": "Test@123",
                "role": "customer",
                "is_logged_in": False,
                "is_blocked": False
            },
            {
                "id": 2,
                "username": "TestOwner",
                "email": "testowner@example.com",
                "password": "Test@123",
                "role": "restaurant owner",
                "is_logged_in": False,
                "is_blocked": False
            }
        ]}))

    test_repo = RestaurantRepository(file_path=str(temp_db))
    test_repo_user = UserRepository(file=str(temp_user_db))
    test_controller = RestaurantController(repo=test_repo)
    


    app.dependency_overrides[get_controller] = lambda: test_controller

    original_repo = auth_dependencies.repo
    auth_dependencies.repo = test_repo_user

    with TestClient(app) as client:
        client.headers.update({"X-User-Id": "2"})
        yield client

    auth_dependencies.repo = original_repo
    app.dependency_overrides.clear()

new_restaurant = {
        "name": "Test Restaurant",
        "cuisine": "Test Cuisine",
        "location": "123 Test St",
        "delivery_fee": 2.99
    }

def test_get_all_restaurants(test_client):
    response = test_client.get("/restaurants/")
    assert response.status_code == 200
    assert isinstance(response.json(), dict) # Should return a paginated response dict

def test_add_restaurant(test_client):
    # The controller should return the new restaurant dict, which the router translates to a 200 response
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_restaurant["name"]
    assert data["cuisine"] == new_restaurant["cuisine"]
    assert data["location"] == new_restaurant["location"]
    assert data["delivery_fee"] == new_restaurant["delivery_fee"]

def test_add_restaurant_missing_fields(test_client):
    incomplete = {"name": "Incomplete Restaurant"}

    # The controller should return an error dict, which the router translates to a 422 response due to Pydantic validation failure
    response = test_client.post("/restaurants/", json=incomplete)
    assert response.status_code == 422  # Pydantic validation error for missing required fields
    data = response.json()
    assert "detail" in data

def test_add_restaurant_invalid_delivery_fee(test_client):
    invalid = new_restaurant.copy()
    invalid["delivery_fee"] = -5.0

    # The controller should return an error dict, which the router translates to a 422 response due to Pydantic validation failure
    response = test_client.post("/restaurants/", json=invalid)
    assert response.status_code == 422  # Pydantic validation error for invalid delivery fee
    data = response.json()
    assert "detail" in data

def test_update_restaurant(test_client):
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # PUT endpoint reads name/delivery_fee as query params, not a JSON body
    update_params = {"name": "Updated Restaurant Name", "delivery_fee": 3.99}
    response = test_client.put(f"/restaurants/{restaurant_id}", params=update_params)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_params["name"]
    assert data["delivery_fee"] == update_params["delivery_fee"]

def test_update_restaurant_no_fields(test_client):
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Try to update with no fields provided
    response = test_client.put(f"/restaurants/{restaurant_id}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

def test_update_restaurant_invalid_delivery_fee(test_client):
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Try to update with an invalid delivery fee
    update_params = {"delivery_fee": -10.0}
    response = test_client.put(f"/restaurants/{restaurant_id}", params=update_params)
    assert response.status_code == 422  # Pydantic validation error for invalid delivery fee
    data = response.json()
    assert "detail" in data

def test_update_restaurant_not_found(test_client):
    # Try to update a restaurant that doesn't exist
    update_params = {"name": "Nonexistent Restaurant"}
    response = test_client.put("/restaurants/9999", params=update_params)
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

def test_update_restaurant_availability_no_menu_items(test_client):
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]
    assert response.json()["is_available"] == False  # New restaurants should start as unavailable

    # Try to mark the restaurant as available when it has no menu items
    update_params = {"is_available": True}
    response = test_client.put(f"/restaurants/{restaurant_id}", params=update_params)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Cannot mark restaurant as available without menu items" in data["detail"]

def test_update_restaurant_availability_with_menu_items(test_client):
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Add a menu item to the restaurant
    menu_item = {
        "name": "Test Menu Item",
        "description": "A menu item for testing",
        "price": 9.99
    }
    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=menu_item)
    assert add_response.status_code == 200

    # Now try to mark the restaurant as available
    update_params = {"is_available": True}
    response = test_client.put(f"/restaurants/{restaurant_id}", params=update_params)
    assert response.status_code == 200
    data = response.json()
    assert data["is_available"] == True

def test_delete_restaurant(test_client):
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Delete the restaurant
    delete_response = test_client.delete(f"/restaurants/{restaurant_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the restaurant should return a 404
    get_response = test_client.get(f"/restaurants/{restaurant_id}")
    assert get_response.status_code == 404

def test_get_restaurant_by_id(test_client):
    # First add a restaurant to ensure there is something to retrieve
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Now try to retrieve that restaurant by ID
    get_response = test_client.get(f"/restaurants/{restaurant_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == restaurant_id
    assert data["name"] == new_restaurant["name"]

def test_get_restaurant_by_id_not_found(test_client):
    # Try to get a restaurant with an ID that doesn't exist
    get_response = test_client.get("/restaurants/9999")
    assert get_response.status_code == 404
    data = get_response.json()
    assert "detail" in data

def test_get_restaurants_by_owner(test_client):
    # Add two restaurants with the same owner_id
    restaurant1 = new_restaurant.copy()
    response1 = test_client.post("/restaurants/", json=restaurant1)
    assert response1.status_code == 200

    restaurant2 = new_restaurant.copy()
    response2 = test_client.post("/restaurants/", json=restaurant2)
    assert response2.status_code == 200

    # Now retrieve restaurants by owner_id 1 (this is the current default owner_id for new restaurants in the controller)
    get_response = test_client.get("/restaurants/owner/1")
    assert get_response.status_code == 200
    data = get_response.json()
    assert isinstance(data, dict) # Should return a paginated response dict
    assert len(data["items"]) == 2
    for rest in data["items"]:
        assert rest["owner_id"] == 1

def test_get_restaurants_by_location(test_client):
    # Add two restaurants with the same location
    restaurant1 = new_restaurant.copy()
    restaurant1["location"] = "Test Location"
    response1 = test_client.post("/restaurants/", json=restaurant1)
    assert response1.status_code == 200

    restaurant2 = new_restaurant.copy()
    restaurant2["location"] = "Test Location"
    response2 = test_client.post("/restaurants/", json=restaurant2)
    assert response2.status_code == 200

    # Add a third restaurant with a different location
    restaurant3 = new_restaurant.copy()
    restaurant3["location"] = "Different Location"
    response3 = test_client.post("/restaurants/", json=restaurant3)
    assert response3.status_code == 200

    # Now retrieve restaurants by location "Test Location"
    get_response = test_client.get("/restaurants/location/Test%20Location")
    assert get_response.status_code == 200
    data = get_response.json()
    assert isinstance(data, dict) # Should return a paginated response dict
    assert len(data["items"]) == 2
    for rest in data["items"]:
        assert rest["location"] == "Test Location"


'''
    Menu item operations for a specific restaurant:
        - Add a menu item to a restaurant
        - Update a menu item from a restaurant
        - Delete a menu item from a restaurant
        - Get menu items for a restaurant
'''

new_menu_item = {
        "name": "Test Menu Item",
        "description": "A menu item for testing",
        "price": 9.99
    }

def test_add_menu_item_to_restaurant(test_client):
    # First add a restaurant to ensure there is something to add a menu item to
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Now try to add a menu item to that restaurant
    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=new_menu_item)
    assert add_response.status_code == 200
    data = add_response.json()
    assert data["name"] == new_menu_item["name"]
    assert data["description"] == new_menu_item["description"]
    assert data["price"] == new_menu_item["price"]

def test_add_menu_item_to_nonexistent_restaurant(test_client):
    # Try to add a menu item to a restaurant ID that doesn't exist
    add_response = test_client.post("/restaurants/9999/menu", json=new_menu_item)
    assert add_response.status_code == 404
    data = add_response.json()
    assert "detail" in data

def test_add_menu_item_invalid_price(test_client):
    # First add a restaurant to ensure there is something to add a menu item to
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Now try to add a menu item with an invalid price
    invalid_menu_item = new_menu_item.copy()
    invalid_menu_item["price"] = -1.0
    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=invalid_menu_item)
    assert add_response.status_code == 422  # Pydantic validation error for invalid price
    data = add_response.json()
    assert "detail" in data

def test_add_menu_item_missing_fields(test_client):
    # First add a restaurant to ensure there is something to add a menu item to
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Now try to add a menu item with missing fields
    incomplete_menu_item = {"name": "Incomplete Menu Item"}
    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=incomplete_menu_item)
    assert add_response.status_code == 422  # Pydantic validation error for missing required fields
    data = add_response.json()
    assert "detail" in data

def test_update_menu_item_from_restaurant(test_client):
    # First add a restaurant and a menu item to ensure there is something to update
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=new_menu_item)
    assert add_response.status_code == 200
    menu_item_id = add_response.json()["id"]

    # Now try to update that menu item
    update_params = {"name": "Updated Menu Item Name", "price": 12.99}
    update_response = test_client.put(f"/restaurants/{restaurant_id}/menu/{menu_item_id}", params=update_params)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == update_params["name"]
    assert data["price"] == update_params["price"]

def test_update_menu_item_invalid_price(test_client):
    # First add a restaurant and a menu item to ensure there is something to update
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=new_menu_item)
    assert add_response.status_code == 200
    menu_item_id = add_response.json()["id"]

    # Now try to update that menu item with an invalid price
    update_params = {"price": -5.0}
    update_response = test_client.put(f"/restaurants/{restaurant_id}/menu/{menu_item_id}", params=update_params)
    assert update_response.status_code == 422  # Pydantic validation error for invalid price
    data = update_response.json()
    assert "detail" in data

def test_update_menu_item_not_found(test_client):
    # First add a restaurant to ensure there is something to update
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Now try to update a menu item that doesn't exist
    update_params = {"name": "Nonexistent Menu Item"}
    update_response = test_client.put(f"/restaurants/{restaurant_id}/menu/9999", params=update_params)
    assert update_response.status_code == 404
    data = update_response.json()
    assert "detail" in data

def test_update_menu_item_restaurant_not_found(test_client):
    # Try to update a menu item for a restaurant that doesn't exist
    update_params = {"name": "Nonexistent Menu Item"}
    update_response = test_client.put("/restaurants/9999/menu/1", params=update_params)
    assert update_response.status_code == 404
    data = update_response.json()
    assert "detail" in data

def test_delete_menu_item_from_restaurant(test_client):
    # First add a restaurant and a menu item to ensure there is something to delete
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=new_menu_item)
    assert add_response.status_code == 200
    menu_item_id = add_response.json()["id"]

    # Now try to delete that menu item
    delete_response = test_client.delete(f"/restaurants/{restaurant_id}/menu/{menu_item_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the menu item should return a 404
    get_response = test_client.get(f"/restaurants/{restaurant_id}/menu/{menu_item_id}")
    assert get_response.status_code == 404

def test_delete_menu_item_restaurant_not_found(test_client):
    # Try to delete a menu item for a restaurant that doesn't exist
    delete_response = test_client.delete("/restaurants/9999/menu/1")
    assert delete_response.status_code == 404
    data = delete_response.json()
    assert "detail" in data

def test_delete_menu_item_not_found(test_client):
    # First add a restaurant to ensure there is something to delete from
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Now try to delete a menu item that doesn't exist
    delete_response = test_client.delete(f"/restaurants/{restaurant_id}/menu/9999")
    assert delete_response.status_code == 404
    data = delete_response.json()
    assert "detail" in data

def test_delete_menu_item_last_item(test_client):
    # First add a restaurant and a menu item to ensure there is something to delete
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]
    assert response.json()["is_available"] == False  # New restaurants should start as unavailable

    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=new_menu_item)
    assert add_response.status_code == 200
    menu_item_id = add_response.json()["id"]

    # After adding a menu item, turn the restaurant to available
    update_params = {"is_available": True}
    update_response = test_client.put(f"/restaurants/{restaurant_id}", params=update_params)
    assert update_response.status_code == 200
    assert update_response.json()["is_available"] == True

    # Now try to delete that menu item, which is the only item in the restaurant's menu
    delete_response = test_client.delete(f"/restaurants/{restaurant_id}/menu/{menu_item_id}")
    assert delete_response.status_code == 200

    # After deletion, the restaurant should be marked as unavailable since it has no menu items
    get_restaurant_response = test_client.get(f"/restaurants/{restaurant_id}")
    assert get_restaurant_response.status_code == 200
    restaurant_data = get_restaurant_response.json()
    assert restaurant_data["is_available"] == False

def test_get_menu_items_by_restaurant_id(test_client):
    # First add a restaurant and a menu item to ensure there is something to retrieve
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    add_response = test_client.post(f"/restaurants/{restaurant_id}/menu", json=new_menu_item)
    assert add_response.status_code == 200

    # Now try to retrieve menu items for that restaurant
    get_response = test_client.get(f"/restaurants/{restaurant_id}/menu")
    assert get_response.status_code == 200
    data = get_response.json()
    assert isinstance(data, dict) # Should return a paginated response dict
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == new_menu_item["name"]

def test_get_menu_items_by_restaurant_id_not_found(test_client):
    # Try to get menu items for a restaurant that doesn't exist
    get_response = test_client.get("/restaurants/9999/menu")
    assert get_response.status_code == 404
    data = get_response.json()
    assert "detail" in data

def test_get_menu_items_by_restaurant_id_no_items(test_client):
    # First add a restaurant to ensure there is something to retrieve from
    response = test_client.post("/restaurants/", json=new_restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Now try to retrieve menu items for that restaurant, which has no items
    get_response = test_client.get(f"/restaurants/{restaurant_id}/menu")
    assert get_response.status_code == 200
    data = get_response.json()
    assert isinstance(data, dict) # Should return a paginated response dict
    assert len(data["items"]) == 0

