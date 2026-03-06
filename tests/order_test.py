import json
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.orders import get_controller
from src.backend.repositories.order_repo import OrderRepository
from src.backend.controllers.order_controller import OrderController


@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real
    data/order.json.  The temp file is deleted automatically after each
    test, so the production database is never touched.
    """
    temp_db = tmp_path / "test_order.json"
    temp_db.write_text(json.dumps([]))

    test_repo = OrderRepository(file_path=str(temp_db))
    test_controller = OrderController()
    test_controller.order_repo = test_repo

    app.dependency_overrides[get_controller] = lambda: test_controller

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

new_order = {
    "id": 1,
    "timestamp": "2026-03-03T00:00:00",
    "customer_id": 1,
    "restaurant_id": 2,
    "status": "pending",
    "total_price": 10,
    "tax": 1,
    "order_items": [
        {"item_id": 101, "quantity": 2, "order_id": 1, "subtotal": 6}
    ]
}

def test_add_order(test_client):
    # The controller should return the new restaurant dict, which the router translates to a 200 response
    response = test_client.post("/order/", json=new_order)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == 1
    assert len(data["order_items"]) == 1
    assert data["order_items"][0]["item_id"] == 101

def test_delete_order(test_client):
    response = test_client.post("/order/", json=new_order)
    assert response.status_code == 200
    order_id = response.json()["id"]

    # Delete order
    delete_response = test_client.delete(f"/order/{order_id}")
    assert delete_response.status_code == 200

    # After deletion, trying to get the order should return a 404
    get_response = test_client.get(f"/order/{order_id}")
    assert get_response.status_code == 404