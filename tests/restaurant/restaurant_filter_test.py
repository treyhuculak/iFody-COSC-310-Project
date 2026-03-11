import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.restaurants import get_controller
from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.controllers.restaurant_controller import RestaurantController


@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real
    data/restaurants.json.  The temp file is deleted automatically after each
    test, so the production database is never touched.
    """
    temp_db = tmp_path / "test_restaurants.json"
    temp_db.write_text(json.dumps([]))

    test_repo = RestaurantRepository(file_path=str(temp_db))
    test_controller = RestaurantController(repo=test_repo)

    app.dependency_overrides[get_controller] = lambda: test_controller

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_filter_restaurants(test_client):
    # Add some test restaurants
    restaurant1 = {
        "name": "Pizza Place",
        "cuisine": "Italian",
        "location": "Downtown",
        "delivery_fee": 3.99
    }
    restaurant2 = {
        "name": "Sushi Spot",
        "cuisine": "Japanese",
        "location": "Uptown",
        "delivery_fee": 5.99
    }
    restaurant3 = {
        "name": "Burger Joint",
        "cuisine": "American",
        "location": "Downtown",
        "delivery_fee": 2.99
    }

    for restaurant in [restaurant1, restaurant2, restaurant3]:
        response = test_client.post("/restaurants/", json=restaurant)
        assert response.status_code == 200

    # Test filtering by cuisine
    response = test_client.get("/restaurants/filter?cuisine=Italian")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Pizza Place"

    # Test filtering by location
    response = test_client.get("/restaurants/filter?location=Downtown")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Test filtering by max delivery fee
    response = test_client.get("/restaurants/filter?max_fee=4.00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_filter_restaurants_combined(test_client):
    # Add some test restaurants
    restaurant1 = {
        "name": "Pizza Place",
        "cuisine": "Italian",
        "location": "Downtown",
        "delivery_fee": 3.99
    }
    restaurant2 = {
        "name": "Sushi Spot",
        "cuisine": "Japanese",
        "location": "Uptown",
        "delivery_fee": 5.99
    }
    restaurant3 = {
        "name": "Burger Joint",
        "cuisine": "American",
        "location": "Downtown",
        "delivery_fee": 2.99
    }

    for restaurant in [restaurant1, restaurant2, restaurant3]:
        response = test_client.post("/restaurants/", json=restaurant)
        assert response.status_code == 200

    # Test filtering by cuisine and location
    response = test_client.get("/restaurants/filter?cuisine=Italian&location=Downtown")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Pizza Place"

    # Test filtering by cuisine and max delivery fee
    response = test_client.get("/restaurants/filter?cuisine=American&max_fee=3.00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Burger Joint"

def test_filter_restaurants_no_matches(test_client):
    # Add some test restaurants
    restaurant1 = {
        "name": "Pizza Place",
        "cuisine": "Italian",
        "location": "Downtown",
        "delivery_fee": 3.99
    }
    restaurant2 = {
        "name": "Sushi Spot",
        "cuisine": "Japanese",
        "location": "Uptown",
        "delivery_fee": 5.99
    }

    for restaurant in [restaurant1, restaurant2]:
        response = test_client.post("/restaurants/", json=restaurant)
        assert response.status_code == 200

    # Test filtering with criteria that match no restaurants
    response = test_client.get("/restaurants/filter?cuisine=Mexican")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

'''
Tests for the menu item filtering functionality.
'''

def test_filter_menu_items(test_client):
    # Add a test restaurant
    restaurant = {
        "name": "Pizza Place",
        "cuisine": "Italian",
        "location": "Downtown",
        "delivery_fee": 3.99
    }
    response = test_client.post("/restaurants/", json=restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Add some menu items to the restaurant
    menu_item1 = {
        "name": "Margherita Pizza",
        "description": "Classic pizza with tomato sauce, mozzarella, and basil.",
        "price": 10.99
    }
    menu_item2 = {
        "name": "Pepperoni Pizza",
        "description": "Pizza topped with pepperoni slices.",
        "price": 12.99
    }
    menu_item3 = {
        "name": "Garlic Bread",
        "description": "Toasted bread with garlic butter.",
        "price": 4.99
    }

    for menu_item in [menu_item1, menu_item2, menu_item3]:
        response = test_client.post(f"/restaurants/{restaurant_id}/menu/", json=menu_item)
        assert response.status_code == 200

    # Test filtering menu items by max price
    response = test_client.get(f"/restaurants/{restaurant_id}/menu/filter?max_price=11.00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_filter_menu_items_no_matches(test_client):
    # Add a test restaurant
    restaurant = {
        "name": "Pizza Place",
        "cuisine": "Italian",
        "location": "Downtown",
        "delivery_fee": 3.99
    }
    response = test_client.post("/restaurants/", json=restaurant)
    assert response.status_code == 200
    restaurant_id = response.json()["id"]

    # Add a menu item to the restaurant
    menu_item = {
        "name": "Margherita Pizza",
        "description": "Classic pizza with tomato sauce, mozzarella, and basil.",
        "price": 10.99
    }
    response = test_client.post(f"/restaurants/{restaurant_id}/menu/", json=menu_item)
    assert response.status_code == 200

    # Test filtering with a max price that matches no items
    response = test_client.get(f"/restaurants/{restaurant_id}/menu/filter?max_price=5.00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
