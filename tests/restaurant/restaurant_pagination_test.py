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
    data/restaurants.json. The temp file is deleted automatically after each
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


@pytest.fixture
def repo(tmp_path):
    temp_db = tmp_path / "test_restaurants_repo.json"
    temp_db.write_text(json.dumps([]))
    return RestaurantRepository(file_path=str(temp_db))


def test_repository_paginate_returns_slice_and_total(repo):
    results = [{"id": i} for i in range(1, 16)]

    items, total = repo._paginate(results, skip=10, limit=10)

    assert total == 15
    assert len(items) == 5
    assert items[0]["id"] == 11
    assert items[-1]["id"] == 15


def test_repository_paginate_empty_results(repo):
    items, total = repo._paginate([], skip=0, limit=10)

    assert total == 0
    assert items == []


def test_controller_build_paginated_response_first_page(repo):
    controller = RestaurantController(repo=repo)

    response = controller._build_paginated_response(
        items=[{"id": 1}, {"id": 2}],
        total=15,
        skip=0,
        limit=10,
    )

    assert response.page == 1
    assert response.page_size == 10
    assert response.total_pages == 2
    assert response.has_next is True
    assert response.has_prev is False


def test_controller_build_paginated_response_last_page(repo):
    controller = RestaurantController(repo=repo)

    response = controller._build_paginated_response(
        items=[{"id": 11}, {"id": 12}, {"id": 13}, {"id": 14}, {"id": 15}],
        total=15,
        skip=10,
        limit=10,
    )

    assert response.page == 2
    assert response.page_size == 10
    assert response.total_pages == 2
    assert response.has_next is False
    assert response.has_prev is True


def test_get_all_restaurants_endpoint_pagination(test_client):
    for i in range(15):
        restaurant_data = {
            "name": f"Test Restaurant {i}",
            "location": "Test Location",
            "cuisine": "Test Cuisine",
            "delivery_fee": 5.0,
        }
        response = test_client.post("/restaurants", json=restaurant_data)
        assert response.status_code == 200

    response = test_client.get("/restaurants")
    assert response.status_code == 200
    page_one = response.json()

    assert page_one["total"] == 15
    assert page_one["page"] == 1
    assert page_one["page_size"] == 10
    assert page_one["total_pages"] == 2
    assert page_one["has_next"] is True
    assert page_one["has_prev"] is False
    assert len(page_one["items"]) == 10

    response = test_client.get("/restaurants?skip=10&limit=10")
    assert response.status_code == 200
    page_two = response.json()

    assert page_two["page"] == 2
    assert page_two["page_size"] == 10
    assert page_two["total_pages"] == 2
    assert page_two["has_next"] is False
    assert page_two["has_prev"] is True
    assert len(page_two["items"]) == 5


def test_get_all_restaurants_endpoint_rejects_invalid_limit(test_client):
    response = test_client.get("/restaurants?skip=0&limit=0")
    assert response.status_code == 422


def test_get_all_restaurants_endpoint_rejects_negative_skip(test_client):
    response = test_client.get("/restaurants?skip=-1&limit=10")
    assert response.status_code == 422


def test_get_all_restaurants_endpoint_rejects_excessive_limit(test_client):
    response = test_client.get("/restaurants?skip=0&limit=101")
    assert response.status_code == 422
