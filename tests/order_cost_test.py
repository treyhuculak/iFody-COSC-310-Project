import json
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.models.order import OrderCreate, OrderStatus, OrderLocation
from src.backend.routers.orders import get_controller
from src.backend.models.order_item import OrderItem
from src.backend.repositories.order_repo import OrderRepository
from src.backend.controllers.order_controller import OrderController
from src.backend.services.order_service import OrderService

@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real
    data/orders.json.  The temp file is deleted automatically after each
    test, so the production database is never touched.
    """
    temp_db = tmp_path / "test_orders.json"
    temp_db.write_text(json.dumps([]))

    test_repo = OrderRepository(file_path=str(temp_db))
    test_controller = OrderController(repo=test_repo)

    app.dependency_overrides[get_controller] = lambda: test_controller

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

order_items = [
    OrderItem(item_id=1, name="Burger", description="A delicious burger", price=10.0, quantity=2),
    OrderItem(item_id=2, name="Fries", description="Crispy fries", price=5.0, quantity=1)
]

order = OrderCreate(customer_id=1, restaurant_id=1, location=OrderLocation.BRITISH_COLUMBIA, order_items=order_items, status=OrderStatus.PENDING)

# Unit tests for OrderService
def test_calculate_order_subtotal():
    order_service = OrderService()
    
    total = order_service.calculate_order_subtotal(order)
    assert total == 25.0

def test_calculate_tax():
    order_service = OrderService()
    
    subtotal = order_service.calculate_order_subtotal(order)
    assert subtotal == 25.0

    tax = order_service.calculate_tax(order, subtotal)
    assert tax == 3.0  # Assuming a tax rate of 12% for British Columbia


# Integration test for OrderController
def test_add_order(test_client):
    # Mock the get_delivery_fee method to return a fixed delivery fee for testing
    with patch('src.backend.services.order_service.OrderService.get_delivery_fee', return_value=5):
        response = test_client.post("/orders/", json=order.model_dump(mode="json"))
        assert response.status_code == 200

        data = response.json()
        assert data["customer_id"] == order.customer_id
        assert data["restaurant_id"] == order.restaurant_id
        assert data["location"] == order.location.value
        assert len(data["order_items"]) == len(order.order_items)
        assert data["subtotal_price"] == 25.0
        assert data["tax"] == 3.0
        assert data["delivery_fee"] == 5.0
        assert data["total_price"] == 25.0 + 3.0 + 5.0

def test_get_delivery_fee():
    order_service = OrderService()
    # Mock the restaurant repository to return a specific delivery fee
    with patch.object(order_service.restaurant_repo, 'get_restaurant_by_id', return_value={"delivery_fee": 7.5}):
        fee = order_service.get_delivery_fee(order)
        assert fee == 7.5

