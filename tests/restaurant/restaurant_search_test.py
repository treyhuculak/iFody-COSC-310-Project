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
    assert len(results) == 2  # Should find Pizza Palace and Pasta Place

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
    assert len(results) == 0  # Should find no matches

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
    assert len(results) == 1  # Should find Taco Town

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
    assert len(results) == 2  # Should find both restaurants

