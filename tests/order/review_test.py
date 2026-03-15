import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.controllers.order_controller import OrderController
from src.backend.repositories.order_repo import OrderRepository
from src.backend.routers.orders import get_controller


@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary orders JSON file.
    We seed one order so review endpoints can be tested independently of
    order-creation validation behavior.
    """
    temp_db = tmp_path / "test_orders.json"
    seeded_orders = [
        {
            "id": 1,
            "customer_id": 1,
            "restaurant_id": 2,
            "status": "pending",
            "location": "BC",
            "order_items": [],
            "timestamp": "2026-03-15T00:00:00",
            "subtotal_price": 0.0,
            "tax": 0.0,
            "delivery_fee": 0.0,
            "total_price": 0.0,
        }
    ]
    temp_db.write_text(json.dumps(seeded_orders), encoding="utf-8")

    test_repo = OrderRepository(file_path=str(temp_db))
    test_controller = OrderController(repo=test_repo)
    app.dependency_overrides[get_controller] = lambda: test_controller

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_add_review_to_order(test_client):
    review_data = {
        "rating": 4,
        "title": "Good food, slow delivery",
        "comment": "Great food, but delivery was slow.",
    }

    review_response = test_client.post("/orders/1/review", json=review_data)
    assert review_response.status_code == 200
    created_review = review_response.json()
    assert created_review["rating"] == review_data["rating"]
    assert created_review["comment"] == review_data["comment"]
    assert created_review["title"] == review_data["title"]


def test_add_review_to_nonexistent_order(test_client):
    review_data = {
        "rating": 5,
        "title": "Excellent!",
        "comment": "Best meal ever!",
    }

    response = test_client.post("/orders/999/review", json=review_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Order with id 999 not found."


def test_add_review_with_invalid_rating(test_client):
    review_data = {
        "rating": 6,
        "title": "Invalid rating",
        "comment": "This review has an invalid rating.",
    }

    review_response = test_client.post("/orders/1/review", json=review_data)
    assert review_response.status_code == 422


def test_add_review_with_missing_fields(test_client):
    review_data = {
        "rating": 4,
    }

    review_response = test_client.post("/orders/1/review", json=review_data)
    assert review_response.status_code == 422


def test_add_review_to_order_with_existing_review(test_client):
    review_data_1 = {
        "rating": 4,
        "title": "Good food",
        "comment": "The food was good.",
    }
    review_response_1 = test_client.post("/orders/1/review", json=review_data_1)
    assert review_response_1.status_code == 200

    review_data_2 = {
        "rating": 2,
        "title": "Changed my mind",
        "comment": "Actually, the food was not that good.",
    }
    review_response_2 = test_client.post("/orders/1/review", json=review_data_2)
    assert review_response_2.status_code == 400
    assert review_response_2.json()["detail"] == "Order with id 1 already has a review."


def test_delete_review_from_order(test_client):
    review_data = {
        "rating": 4,
        "title": "Good food",
        "comment": "The food was good.",
    }
    review_response = test_client.post("/orders/1/review", json=review_data)
    assert review_response.status_code == 200

    delete_response = test_client.delete("/orders/1/review")
    assert delete_response.status_code == 200


def test_delete_nonexistent_review(test_client):
    delete_response = test_client.delete("/orders/1/review")
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Review for order with id 1 not found."


def test_update_review_from_order(test_client):
    review_data = {
        "rating": 4,
        "title": "Good food",
        "comment": "The food was good.",
    }
    review_response = test_client.post("/orders/1/review", json=review_data)
    assert review_response.status_code == 200

    updated_review_data = {
        "rating": 5,
        "title": "Actually it was great",
        "comment": "I changed my mind the food was great",
    }
    update_response = test_client.put("/orders/1/review", json=updated_review_data)
    assert update_response.status_code == 200
    updated_review = update_response.json()
    assert updated_review["rating"] == updated_review_data["rating"]
    assert updated_review["comment"] == updated_review_data["comment"]
    assert updated_review["title"] == updated_review_data["title"]


def test_update_nonexistent_review_creates_review(test_client):
    updated_review_data = {
        "rating": 5,
        "title": "Nonexistent review",
        "comment": "Trying to update a review that doesn't exist.",
    }

    update_response = test_client.put("/orders/1/review", json=updated_review_data)
    assert update_response.status_code == 200
    created_review = update_response.json()
    assert created_review["title"] == updated_review_data["title"]


def test_get_review_from_order(test_client):
    review_data = {
        "rating": 4,
        "title": "Good food",
        "comment": "The food was good.",
    }
    review_response = test_client.post("/orders/1/review", json=review_data)
    assert review_response.status_code == 200

    get_response = test_client.get("/orders/1/review")
    assert get_response.status_code == 200
    retrieved_review = get_response.json()
    assert retrieved_review["rating"] == review_data["rating"]
    assert retrieved_review["comment"] == review_data["comment"]
    assert retrieved_review["title"] == review_data["title"]


def test_get_nonexistent_review(test_client):
    get_response = test_client.get("/orders/1/review")
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Review for order with id 1 not found."

def test_add_review_too_long_fields(test_client):
    review_data = {
        "rating": 4,
        "title": "Good food",
        "comment": "A" * 501,  # 501 characters, exceeding the 500 character limit
    }
    review_response = test_client.post("/orders/1/review", json=review_data)
    assert review_response.status_code == 422

    review_data["title"] = "T" * 51  # 51 characters, exceeding the 50 character limit
    review_data["comment"] = "Valid comment"
    review_response = test_client.post("/orders/1/review", json=review_data)
    assert review_response.status_code == 422

def test_timestamps_are_set_on_review_creation(test_client):
    review_data = {
        "rating": 4,
        "title": "Good food",
        "comment": "The food was good.",
    }
    review_response = test_client.post("/orders/1/review", json=review_data)
    assert review_response.status_code == 200
    created_review = review_response.json()
    assert "created_at" in created_review
    assert "updated_at" in created_review
    assert created_review["created_at"] == created_review["updated_at"]

def test_timestamps_are_updated_on_review_update(test_client):
    review_data = {
        "rating": 4,
        "title": "Good food",
        "comment": "The food was good.",
    }
    review_response = test_client.post("/orders/1/review", json=review_data)
    assert review_response.status_code == 200
    created_review = review_response.json()

    updated_review_data = {
        "rating": 5,
        "title": "Actually it was great",
        "comment": "I changed my mind the food was great",
    }
    update_response = test_client.put("/orders/1/review", json=updated_review_data)
    assert update_response.status_code == 200
    updated_review = update_response.json()
    assert updated_review["updated_at"] != created_review["updated_at"]
    assert updated_review["created_at"] == created_review["created_at"]
    assert updated_review["updated_at"] > created_review["created_at"]
