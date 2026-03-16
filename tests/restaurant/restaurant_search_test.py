import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
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
                "username": "Testowner",
                "email": "testowner@example.com",
                "password": "Test@123",
                "role": "restaurant owner",
                "is_logged_in": False,
                "is_blocked": False
            }
        ]}))

    test_repo = RestaurantRepository(file_path=str(temp_db))
    test_user_repo = UserRepository(file=str(temp_user_db))
    test_controller = RestaurantController(repo=test_repo)

    app.dependency_overrides[get_controller] = lambda: test_controller

    original_repo = auth_dependencies.repo
    auth_dependencies.repo = test_user_repo

    with TestClient(app) as client:
        client.headers.update({"X-User-Id": "1"})
        yield client

    auth_dependencies.repo = original_repo
    app.dependency_overrides.clear()

def test_search_restaurants_by_partial_name(test_client):
    # First, add some restaurants to search through
    restaurant1 = {
        "name": "Pizza Palace",
        "cuisine": "Italian",
        "location": "Downtown",
        "delivery_fee": 3.99
    }
    restaurant2 = {
        "name": "Burger Barn",
        "cuisine": "American",
        "location": "Uptown",
        "delivery_fee": 2.99
    }
    restaurant3 = {
        "name": "Pasta Place",
        "cuisine": "Italian",
        "location": "Midtown",
        "delivery_fee": 4.99
    }
    test_client.post("/restaurants/", json=restaurant1)
    test_client.post("/restaurants/", json=restaurant2)
    test_client.post("/restaurants/", json=restaurant3)

    # Now search for restaurants with 'P' in the name
    response = test_client.get("/restaurants/search/?name=P")
    assert response.status_code == 200
    results = response.json()
    assert len(results["items"]) == 2  # Should find Pizza Palace and Pasta Place

def test_search_restaurants_by_partial_name_no_matches(test_client):
    # Add a restaurant to search through
    restaurant = {
        "name": "Sushi Spot",
        "cuisine": "Japanese",
        "location": "Downtown",
        "delivery_fee": 5.99
    }
    test_client.post("/restaurants/", json=restaurant)

    # Now search for restaurants with 'X' in the name (should find none)
    response = test_client.get("/restaurants/search/?name=X")
    assert response.status_code == 200
    results = response.json()
    assert len(results["items"]) == 0  # Should find no matches

def test_search_restaurants_by_partial_name_case_insensitive(test_client):
    # Add a restaurant to search through
    restaurant = {
        "name": "Taco Town",
        "cuisine": "Mexican",
        "location": "Uptown",
        "delivery_fee": 2.49
    }
    test_client.post("/restaurants/", json=restaurant)

    # Now search for restaurants with 't' in the name (should find Taco Town)
    response = test_client.get("/restaurants/search/?name=t")
    assert response.status_code == 200
    results = response.json()
    assert len(results["items"]) == 1  # Should find Taco Town

def test_search_restaurants_by_partial_name_empty_string(test_client):
    # Add some restaurants to search through
    restaurant1 = {
        "name": "Noodle Nook",
        "cuisine": "Asian",
        "location": "Downtown",
        "delivery_fee": 3.49
    }
    restaurant2 = {
        "name": "Salad Stop",
        "cuisine": "Healthy",
        "location": "Uptown",
        "delivery_fee": 1.99
    }
    test_client.post("/restaurants/", json=restaurant1)
    test_client.post("/restaurants/", json=restaurant2)

    # Now search with an empty string (should return all restaurants)
    response = test_client.get("/restaurants/search/?name=")
    assert response.status_code == 200
    results = response.json()
    assert len(results["items"]) == 2  # Should find both restaurants

def test_search_restaurants_by_partial_name_whitespace_handling(test_client):
    # Add a restaurant to search through
    restaurant = {
        "name": "BBQ Bistro",
        "cuisine": "Barbecue",
        "location": "Midtown",
        "delivery_fee": 4.49
    }
    test_client.post("/restaurants/", json=restaurant)

    # Now search for restaurants with '  bbq  ' in the name (should find BBQ Bistro, ignoring extra whitespace)
    response = test_client.get("/restaurants/search/?name=  bbq  ")
    assert response.status_code == 200
    results = response.json()
    assert len(results["items"]) == 1  # Should find BBQ Bistro

'''
Tests for searching menu items by partial name within a specific restaurant.  
This covers the new search endpoint added to the restaurant controller and router.
'''

def test_search_menu_items_by_partial_name(test_client):
    # First, add a restaurant and some menu items to search through
    restaurant = {
        "name": "BBQ Joint",
        "cuisine": "Barbecue",
        "location": "Downtown",
        "delivery_fee": 4.99
    }
    response = test_client.post("/restaurants/", json=restaurant)
    restaurant_id = response.json()["id"]

    menu_item1 = {
        "name": "Pulled Pork Sandwich",
        "description": "Slow-cooked pulled pork on a bun",
        "price": 8.99
    }
    menu_item2 = {
        "name": "Brisket Plate",
        "description": "Smoked brisket served with sides",
        "price": 12.99
    }
    menu_item3 = {
        "name": "BBQ Chicken Wings",
        "description": "Spicy BBQ glazed wings",
        "price": 9.99
    }
    test_client.post(f"/restaurants/{restaurant_id}/menu", json=menu_item1)
    test_client.post(f"/restaurants/{restaurant_id}/menu", json=menu_item2)
    test_client.post(f"/restaurants/{restaurant_id}/menu", json=menu_item3)

    # Now search for menu items with 'P' in the name (should find Pulled Pork Sandwich and Brisket Plate)
    response = test_client.get(f"/restaurants/{restaurant_id}/menu/search/?name=P")
    assert response.status_code == 200
    results = response.json()
    assert len(results["items"]) == 2  # Should find Pulled Pork Sandwich and Brisket Plate

def test_search_menu_items_by_partial_name_no_matches(test_client):
    # Add a restaurant and a menu item to search through
    restaurant = {
        "name": "Vegan Cafe",
        "cuisine": "Vegan",
        "location": "Uptown",
        "delivery_fee": 3.49
    }
    response = test_client.post("/restaurants/", json=restaurant)
    restaurant_id = response.json()["id"]

    menu_item = {
        "name": "Avocado Toast",
        "description": "Smashed avocado on whole grain toast",
        "price": 6.99
    }
    test_client.post(f"/restaurants/{restaurant_id}/menu", json=menu_item)

    # Now search for menu items with 'X' in the name (should find none)
    response = test_client.get(f"/restaurants/{restaurant_id}/menu/search/?name=X")
    assert response.status_code == 200
    results = response.json()
    assert len(results["items"]) == 0  # Should find no matches

def test_search_menu_items_by_partial_name_case_insensitive(test_client):
    # Add a restaurant and a menu item to search through
    restaurant = {
        "name": "Dessert Den",
        "cuisine": "Desserts",
        "location": "Midtown",
        "delivery_fee": 2.99
    }
    response = test_client.post("/restaurants/", json=restaurant)
    restaurant_id = response.json()["id"]

    menu_item = {
        "name": "Chocolate Cake",
        "description": "Rich chocolate layer cake",
        "price": 5.99
    }
    test_client.post(f"/restaurants/{restaurant_id}/menu", json=menu_item)

    # Now search for menu items with 'c' in the name (should find Chocolate Cake)
    response = test_client.get(f"/restaurants/{restaurant_id}/menu/search/?name=c")
    assert response.status_code == 200
    results = response.json()
    assert len(results["items"]) == 1  # Should find Chocolate Cake

def test_search_menu_items_by_partial_name_empty_string(test_client):
    # Add a restaurant and some menu items to search through
    restaurant = {
        "name": "Breakfast Bistro",
        "cuisine": "Breakfast",
        "location": "Downtown",
        "delivery_fee": 3.99
    }
    response = test_client.post("/restaurants/", json=restaurant)
    restaurant_id = response.json()["id"]

    menu_item1 = {
        "name": "Pancakes",
        "description": "Fluffy pancakes with syrup",
        "price": 7.99
    }
    menu_item2 = {
        "name": "Omelette",
        "description": "Three-egg omelette with cheese",
        "price": 8.99
    }
    test_client.post(f"/restaurants/{restaurant_id}/menu", json=menu_item1)
    test_client.post(f"/restaurants/{restaurant_id}/menu", json=menu_item2)

    # Now search with an empty string (should return all menu items)
    response = test_client.get(f"/restaurants/{restaurant_id}/menu/search/?name=")
    assert response.status_code == 200
    results = response.json()
    assert len(results["items"]) == 2  # Should find both menu items

def test_search_menu_items_by_partial_name_nonexistent_restaurant(test_client):
    # Search for menu items in a restaurant that doesn't exist (should return 404)
    response = test_client.get("/restaurants/999/menu/search/?name=anything")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant with id 999 not found."

def test_search_menu_items_by_partial_name_whitespace_handling(test_client):
    # Add a restaurant and some menu items to search through
    restaurant = {
        "name": "Grill House",
        "cuisine": "Grilled Foods",
        "location": "Uptown",
        "delivery_fee": 4.49
    }
    response = test_client.post("/restaurants/", json=restaurant)
    restaurant_id = response.json()["id"]

    menu_item1 = {
        "name": "Grilled Cheese Sandwich",
        "description": "Melted cheese between toasted bread",
        "price": 6.99
    }
    menu_item2 = {
        "name": "Grilled Chicken Salad",
        "description": "Fresh salad topped with grilled chicken",
        "price": 9.99
    }
    test_client.post(f"/restaurants/{restaurant_id}/menu", json=menu_item1)
    test_client.post(f"/restaurants/{restaurant_id}/menu", json=menu_item2)

    # Now search for menu items with '  grilled  ' in the name (should find both items, ignoring extra whitespace)
    response = test_client.get(f"/restaurants/{restaurant_id}/menu/search/?name=  grilled  ")
    assert response.status_code == 200
    results = response.json()
    assert len(results["items"]) == 2  # Should find both menu items