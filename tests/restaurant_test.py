import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

# Will fill out when implementing the restaurant controller methods and routes. Just base methods etc for now.

# client = TestClient(app)

# def test_create_restaurant():
#     # Test creating a new restaurant
#     response = client.post("/restaurants/", json={
#         "name": "Test Restaurant",
#         "status": "open",
#         "location": "123 Test St",
#         "delivery_fee": 5.0,
#         "owner_id": 1
#     })
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "Test Restaurant"
#     assert data["status"] == "open"
#     assert data["delivery_fee"] == 5.0
#     assert data["owner_id"] == 1