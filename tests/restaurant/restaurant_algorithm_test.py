import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.backend.main import app
from src.backend.controllers.restaurant_controller import RestaurantController
from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.routers.restaurants import get_controller


def _restaurant(restaurant_id: int, name: str, city: str = "testCity") -> dict:
    return {
        "id": restaurant_id,
        "name": name,
        "cuisine": "test cuisine",
        "city": city,
        "province": "BC",
        "delivery_fee": 5.0,
        "is_available": True,
        "owner_id": 2,
        "menu_items": [
            {
                "id": 1,
                "name": "test item",
                "description": "test item description",
                "price": 10.0,
            }
        ],
    }


@pytest.fixture
def repo() -> RestaurantRepository:
    # File reads are mocked in each test.
    return RestaurantRepository(file_path="data/restaurants.json")


def test_popular_restaurants_sorted_by_order_count(repo):
    '''
    Unit test for the get_popular_restaurants_in_location method of the RestaurantRepository class.
    This test verifies that the method correctly returns restaurants sorted by the number of orders in a given location.
    '''
    restaurants = [
        _restaurant(1, "A"),
        _restaurant(2, "B"),
        _restaurant(3, "C", city="other city"),
    ]
    orders = [
        {"restaurant_id": 2},
        {"restaurant_id": 2},
        {"restaurant_id": 1},
        {"restaurant_id": 3},
    ]

    with patch.object(repo, "_get_all_restaurants", return_value=restaurants), patch.object(
        repo.order_repo, "_get_all_orders", return_value=orders
    ):
        items, total = repo.get_popular_restaurants_in_location("testCity")

    assert total == 2
    assert [restaurant["id"] for restaurant in items] == [2, 1]


def test_recent_restaurants_follow_recent_id_order(repo):
    '''
    Unit test for the get_recently_ordered_from_restaurants method of the RestaurantRepository class.
    This test verifies that the method returns recently ordered restaurants in the order they were most recently ordered from, without duplicates.
    '''
    restaurants = [
        _restaurant(1, "A"),
        _restaurant(2, "B"),
        _restaurant(3, "C"),
    ]

    with patch.object(repo, "_get_all_restaurants", return_value=restaurants), patch.object(
        repo.order_repo, "get_recently_ordered_from_restaurants", return_value=[3, 1]
    ):
        items, total = repo.get_recently_ordered_from_restaurants(customer_id=1)

    assert total == 2
    assert [restaurant["id"] for restaurant in items] == [3, 1]


def test_popular_restaurants_no_orders_returns_empty_list(repo):
    '''
    Unit test for the get_popular_restaurants_in_location method of the RestaurantRepository class.
    This test verifies that the method returns an empty list when there are no orders for restaurants in the specified location.
    '''
    restaurants = [
        _restaurant(1, "A"),
        _restaurant(2, "B"),
        _restaurant(3, "C", city="other city"),
    ]
    orders = []

    with patch.object(repo, "_get_all_restaurants", return_value=restaurants), patch.object(
        repo.order_repo, "_get_all_orders", return_value=orders
    ):
        items, total = repo.get_popular_restaurants_in_location("testCity")

    assert total == 0
    assert items == []


def test_recent_restaurants_no_orders_returns_empty_list(repo):
    '''
    Unit test for the get_recently_ordered_from_restaurants method of the RestaurantRepository class.
    This test verifies that the method returns an empty list when there are no recent orders for the customer.
    '''
    restaurants = [
        _restaurant(1, "A"),
        _restaurant(2, "B"),
        _restaurant(3, "C"),
    ]

    with patch.object(repo, "_get_all_restaurants", return_value=restaurants), patch.object(
        repo.order_repo, "get_recently_ordered_from_restaurants", return_value=[]
    ):
        items, total = repo.get_recently_ordered_from_restaurants(customer_id=1)

    assert total == 0
    assert items == []


@pytest.fixture
def test_client_with_mock_controller():
    mock_controller = Mock()
    mock_controller.get_get_popular_restaurants_in_location.return_value = {
        "items": [_restaurant(2, "Popular One")],
        "total": 1,
        "page": 1,
        "page_size": 5,
        "total_pages": 1,
        "has_next": False,
        "has_prev": False,
    }
    mock_controller.get_recently_ordered_from_restaurants.return_value = {
        "items": [_restaurant(3, "Recent One")],
        "total": 1,
        "page": 1,
        "page_size": 5,
        "total_pages": 1,
        "has_next": False,
        "has_prev": False,
    }

    app.dependency_overrides[get_controller] = lambda: mock_controller

    with TestClient(app) as client:
        yield client, mock_controller

    app.dependency_overrides.clear()


def test_popular_restaurants_endpoint_uses_controller(test_client_with_mock_controller):
    '''
    Integration test that verifies that the /restaurants/popular endpoint correctly uses the restaurant controller to fetch popular restaurants based on location.
    The test sets up a mock controller that returns a predefined response when the get_get_popular_restaurants_in_location method is called. 
    It then makes a request to the endpoint with a specific location and checks that the response contains the expected restaurant data and that the controller 
    method was called with the correct parameters.
    '''
    client, mock_controller = test_client_with_mock_controller

    response = client.get("/restaurants/popular/testCity", params={"skip": 0, "limit": 5})

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"][0]["name"] == "Popular One"
    mock_controller.get_get_popular_restaurants_in_location.assert_called_once_with(
        location="testCity", skip=0, limit=5
    )


def test_recent_restaurants_endpoint_uses_active_user_header(test_client_with_mock_controller):
    '''
    Integration test that verifies that the /restaurants/recent endpoint correctly uses the active user ID from the request header to fetch recently ordered restaurants.
    The test sets up a mock controller that returns a predefined response when the get_recently_ordered_from_restaurants method is called. 
    It then makes a request to the endpoint with a specific user ID in the header and checks that the response contains the expected restaurant data and that the 
    controller method was called with the correct user ID.
    '''
    client, mock_controller = test_client_with_mock_controller

    response = client.get("/restaurants/recent", headers={"X-User-Id": "42"}, params={"skip": 0, "limit": 5})

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"][0]["name"] == "Recent One"
    mock_controller.get_recently_ordered_from_restaurants.assert_called_once_with(
        customer_id=42, skip=0, limit=5
    )


@pytest.fixture
def test_client_with_real_controller(repo):
    real_controller = RestaurantController(repo=repo)
    app.dependency_overrides[get_controller] = lambda: real_controller

    with TestClient(app) as client:
        yield client, repo

    app.dependency_overrides.clear()


def test_popular_endpoint_returns_most_to_least_popular(test_client_with_real_controller):
    '''
    Integration test that verifies that the /restaurants/popular endpoint returns restaurants in order of popularity based on the number of orders.
    The test sets up a scenario where three restaurants have different numbers of orders, and it checks that the endpoint returns them in the correct order from most popular to least popular.
    '''
    client, repo = test_client_with_real_controller
    restaurants = [
        _restaurant(1, "One"),
        _restaurant(2, "Two"),
        _restaurant(3, "Three"),
    ]
    orders = [
        {"restaurant_id": 3},
        {"restaurant_id": 2},
        {"restaurant_id": 3},
        {"restaurant_id": 3},
        {"restaurant_id": 1},
        {"restaurant_id": 2},
    ]

    with patch.object(repo, "_get_all_restaurants", return_value=restaurants), patch.object(
        repo.order_repo, "_get_all_orders", return_value=orders
    ):
        response = client.get("/restaurants/popular/testCity")

    assert response.status_code == 200
    payload = response.json()
    assert [restaurant["id"] for restaurant in payload["items"]] == [3, 2, 1]


def test_recent_endpoint_returns_most_recent_to_least_recent(test_client_with_real_controller):
    '''
    Integration test that verifies that the /restaurants/recent endpoint returns restaurants in the order they were most recently ordered from.
    The test sets up a scenario where a customer has ordered from three restaurants at different times.
    '''
    client, repo = test_client_with_real_controller
    restaurants = [
        _restaurant(1, "One"),
        _restaurant(2, "Two"),
        _restaurant(3, "Three"),
    ]
    orders_for_customer = [
        {"restaurant_id": 1, "timestamp": "2026-03-01T10:00:00"},
        {"restaurant_id": 2, "timestamp": "2026-03-01T10:05:00"},
        {"restaurant_id": 1, "timestamp": "2026-03-01T10:10:00"},
        {"restaurant_id": 3, "timestamp": "2026-03-01T10:15:00"},
    ]

    with patch.object(repo, "_get_all_restaurants", return_value=restaurants), patch.object(
        repo.order_repo, "get_orders_by_customer_id", return_value=orders_for_customer
    ):
        response = client.get("/restaurants/recent", headers={"X-User-Id": "7"})

    assert response.status_code == 200
    payload = response.json()
    assert [restaurant["id"] for restaurant in payload["items"]] == [3, 1, 2]



