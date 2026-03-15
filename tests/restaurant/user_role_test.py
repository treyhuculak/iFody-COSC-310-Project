import json
from fastapi import Header
import pytest

from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.routers.restaurants import get_controller as get_restaurant_controller
from src.backend.routers.orders import get_controller as get_order_controller
from src.backend.routers.restaurants import get_user_id_from_auth
from src.backend.controllers.restaurant_controller import RestaurantController
from src.backend.controllers.order_controller import OrderController
from src.backend.controllers.notification_controller import NotificationController

from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.repositories.order_repo import OrderRepository
from src.backend.repositories.notification_repo import NotificationRepository
from src.backend.repositories.user_repo import UserRepository

import src.backend.utils.auth_dependencies as auth_dependencies


@pytest.fixture
def test_client(tmp_path):
    """
    This provides a temporary environment using JSON files stored in temporary directory
    for testing restaurant and order router and keeps testing data isolated from the actual data files.

    Each test run starts with clean files.
    """

    temp_restaurants = tmp_path / "restaurants.json"
    temp_restaurants.write_text(json.dumps([]))

    temp_orders = tmp_path / "orders.json"
    temp_orders.write_text(json.dumps([]))

    temp_notifications = tmp_path / "notifications.json"
    temp_notifications.write_text(json.dumps([]))

    temp_users = tmp_path / "users.json"
    temp_users.write_text(json.dumps({
        "Users": [
            {
                "id": 1,
                "username": "TestCustomer",
                "email": "testcustomer@123.com",
                "password": "Test@123",
                "role": "customer",
                "is_logged_in": False,
                "is_blocked": False
            },
            {
                "id": 2,
                "username": "TestOwner",
                "email": "testowner@123.com",
                "password": "Test@123",
                "role": "restaurant owner",
                "is_logged_in": False,
                "is_blocked": False
            }

        ]
    }))

    restaurant_repo = RestaurantRepository(file_path=str(temp_restaurants))
    order_repo = OrderRepository(file_path=str(temp_orders))
    notif_repo = NotificationRepository(file_path=str(temp_notifications))
    user_repo = UserRepository(file=str(temp_users))

    notif_controller = NotificationController(repo=notif_repo)
    restaurant_controller = RestaurantController(repo=restaurant_repo)
    order_controller = OrderController(repo=order_repo, notif_controller=notif_controller)


    app.dependency_overrides[get_restaurant_controller] = lambda: restaurant_controller
    app.dependency_overrides[get_order_controller] = lambda: order_controller

    def override_get_user_id_from_auth(x_user_id: int = Header(..., alias="X-User-Id")):
        return x_user_id
    
    app.dependency_overrides[get_user_id_from_auth] = override_get_user_id_from_auth

    original_repo = auth_dependencies.repo
    auth_dependencies.repo = user_repo

    with TestClient(app) as client:
        yield client

    auth_dependencies.repo = original_repo
    app.dependency_overrides.clear()


def test_print_user_1(test_client):
    user = auth_dependencies.repo.get_user_by_id(1)
    assert user is not None

def test_print_user_2(test_client):
    user = auth_dependencies.repo.get_user_by_id(2)
    assert user is not None

def test_missing_header_cannot_add_restaurant(test_client):
    response = test_client.post(
        "/restaurants/",
        json={
            "name": "Test Restaurant",
            "cuisine": "Itlaian",
            "location": "Kelwona",
            "delivery_fee": 5.0
    })
    assert response.status_code == 422

def test_customer_cannot_add_restaurant(test_client):
    response = test_client.post(
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

def test_owner_can_add_restaurant(test_client):
    response = test_client.post(
        "/restaurants/",
        json={
            "name": "Test Restaurant",
            "cuisine": "Itlaian",
            "location": "Kelwona",
            "delivery_fee": 5.0
    },
    headers={"X-User-Id": "2"} # user 2 is a restaurant owner
    )
    print(response.status_code)
    print(response.text)
    assert response.status_code == 200

def test_owner_cannot_add_order(test_client):
    response = test_client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "restaurant_id": 1,
            "location": "BC",
            "order_items": []
        },
        headers={"X-User-Id": "2"}  # user 2 is a restaurant owner
    )
    print(response.status_code)
    print(response.text)
    assert response.status_code == 403

def test_customer_can_add_order(test_client):
    response = test_client.post(
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
