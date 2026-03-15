import json
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.controllers.restaurant_controller import RestaurantController
from src.backend.repositories.order_repo import OrderRepository
from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.routers.restaurants import get_controller


class TestRestaurantRatingUnit:
    def test_calculate_restaurant_rating_returns_zero_when_no_reviews(self):
        mock_repo = MagicMock()
        mock_repo.get_reviews_by_restaurant_id.return_value = []

        controller = RestaurantController(repo=mock_repo)

        assert controller.calculate_restaurant_rating(restaurant_id=1) == 0.0

    def test_calculate_restaurant_rating_returns_average_rounded(self):
        mock_repo = MagicMock()
        mock_repo.get_reviews_by_restaurant_id.return_value = [
            {"rating": 5},
            {"rating": 4},
            {"rating": 4},
        ]

        controller = RestaurantController(repo=mock_repo)

        assert controller.calculate_restaurant_rating(restaurant_id=1) == 4.3


@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by temporary restaurants and orders JSON files.
    This enables endpoint-level tests without relying on production data files.
    """
    temp_restaurants_db = tmp_path / "test_restaurants.json"
    temp_restaurants_db.write_text(
        json.dumps(
            [
                {
                    "id": 2,
                    "name": "Sample Restaurant",
                    "cuisine": "Fusion",
                    "location": "Vancouver",
                    "delivery_fee": 3.5,
                    "is_available": True,
                    "owner_id": 2,
                    "menu_items": [],
                }
            ]
        ),
        encoding="utf-8",
    )

    temp_orders_db = tmp_path / "test_orders.json"
    temp_orders_db.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "customer_id": 1,
                    "restaurant_id": 2,
                    "status": "delivered",
                    "location": "BC",
                    "order_items": [],
                    "timestamp": "2026-03-15T00:00:00",
                    "subtotal_price": 20.0,
                    "tax": 2.4,
                    "delivery_fee": 3.5,
                    "total_price": 25.9,
                    "review": {
                        "rating": 5,
                        "title": "Great",
                        "comment": "Loved it",
                        "created_at": "2026-03-15T00:00:00",
                        "updated_at": "2026-03-15T00:00:00",
                    },
                },
                {
                    "id": 2,
                    "customer_id": 1,
                    "restaurant_id": 2,
                    "status": "delivered",
                    "location": "BC",
                    "order_items": [],
                    "timestamp": "2026-03-15T00:00:00",
                    "subtotal_price": 10.0,
                    "tax": 1.2,
                    "delivery_fee": 3.5,
                    "total_price": 14.7,
                    "review": {
                        "rating": 3,
                        "title": "Okay",
                        "comment": "Average meal",
                        "created_at": "2026-03-15T00:00:00",
                        "updated_at": "2026-03-15T00:00:00",
                    },
                },
            ]
        ),
        encoding="utf-8",
    )

    test_repo = RestaurantRepository(file_path=str(temp_restaurants_db))
    test_repo.order_repo = OrderRepository(file_path=str(temp_orders_db))
    test_controller = RestaurantController(repo=test_repo)

    app.dependency_overrides[get_controller] = lambda: test_controller

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_get_restaurant_rating_endpoint_returns_average(test_client):
    response = test_client.get("/restaurants/2/rating")

    assert response.status_code == 200
    assert response.json() == 4.0


def test_get_restaurant_reviews_endpoint_returns_paginated_reviews(test_client):
    response = test_client.get("/restaurants/2/reviews")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert len(payload["items"]) == 2
    assert payload["items"][0]["title"] == "Great"


def test_get_restaurant_rating_endpoint_returns_zero_without_reviews(tmp_path):
    temp_restaurants_db = tmp_path / "test_restaurants_no_reviews.json"
    temp_restaurants_db.write_text(
        json.dumps(
            [
                {
                    "id": 10,
                    "name": "No Reviews Place",
                    "cuisine": "Cafe",
                    "location": "Kelowna",
                    "delivery_fee": 2.0,
                    "is_available": True,
                    "owner_id": 2,
                    "menu_items": [],
                }
            ]
        ),
        encoding="utf-8",
    )

    temp_orders_db = tmp_path / "test_orders_no_reviews.json"
    temp_orders_db.write_text(json.dumps([]), encoding="utf-8")

    test_repo = RestaurantRepository(file_path=str(temp_restaurants_db))
    test_repo.order_repo = OrderRepository(file_path=str(temp_orders_db))
    test_controller = RestaurantController(repo=test_repo)

    app.dependency_overrides[get_controller] = lambda: test_controller

    with TestClient(app) as client:
        response = client.get("/restaurants/10/rating")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == 0.0
