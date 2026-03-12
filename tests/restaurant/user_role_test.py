from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.repositories.user_repo import UserRepository


client = TestClient(app)

def test_print_user_1():
    repo = UserRepository()
    user = repo.get_user_by_id(1)
    print(user)
    assert user is not None

def test_print_user_2():
    repo = UserRepository()
    user = repo.get_user_by_id(2)
    print(user)
    assert user is not None

def test_missing_header_cannot_add_restaurant():
    response = client.post(
        "/restaurants/",
        json={
            "name": "Test Restaurant",
            "cuisine": "Itlaian",
            "location": "Kelwona",
            "delivery_fee": 5.0
    })
    assert response.status_code == 422

def test_customer_cannot_add_restaurant():
    response = client.post(
        "/restaurants/",
        json={
            "name": "Test Restaurant",
            "cuisine": "Itlaian",
            "location": "Kelwona",
            "delivery_fee": 5.0
    },
    headers={"X-User-Id": "1"} # user 1 is a customer
    )
    assert response.status_code == 403

def test_owner_can_add_restaurant():
    response = client.post(
        "/restaurants/",
        json={
            "name": "Test Restaurant",
            "cuisine": "Itlaian",
            "location": "Kelwona",
            "delivery_fee": 5.0
    },
    headers={"X-User-Id": "2"} # user 2 is a restaurant owner
    )
    assert response.status_code == 200

def test_owner_cannot_add_order():
    response = client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "restaurant_id": 1,
            "location": "BC",
            "order_items": []
        },
        headers={"X-User-Id": "2"}  # user 2 is a restaurant owner
    )
    assert response.status_code == 403

def test_customer_can_add_order():
    response = client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "restaurant_id": 1,
            "location": "BC",
            "order_items": []
        },
        headers={"X-User-Id": "1"}  # user 1 is a customer
    )
    assert response.status_code == 200