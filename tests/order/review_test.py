import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.orders import get_controller
from src.backend.repositories.order_repo import OrderRepository
from src.backend.controllers.order_controller import OrderController
from src.backend.models.order import OrderCreate, OrderStatus, OrderLocation

@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real
    data/reviews.json.  The temp file is deleted automatically after each
    test, so the production database is never touched.
    """
    temp_db = tmp_path / "test_reviews.json"
    temp_db.write_text(json.dumps([]))

    test_repo = OrderRepository(file_path=str(temp_db))
    test_controller = OrderController(repo=test_repo)

    app.dependency_overrides[get_controller] = lambda: test_controller

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

def test_add_review_to_order(test_client):
    # First, create an order to review
    new_order = {
        "customer_id": 1,
        "restaurant_id": 2, 
        "status": OrderStatus.PENDING.value,
        "location": OrderLocation.BRITISH_COLUMBIA.value,
        "order_items": [
            {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
        ]
    }
    response = test_client.post("/orders/", json=new_order)
    assert response.status_code == 200
    created_order = response.json()
    order_id = created_order["id"]

    # Now add a review for that order
    review_data = {
        "rating": 4,
        "title": "Good food, slow delivery",
        "comment": "Great food, but delivery was slow."
    }
    review_response = test_client.post(f"/orders/{order_id}/review", json=review_data)
    assert review_response.status_code == 200
    created_review = review_response.json()
    assert created_review["rating"] == review_data["rating"]
    assert created_review["comment"] == review_data["comment"]
    assert created_review["title"] == review_data["title"]