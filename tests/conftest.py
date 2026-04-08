import json
import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.repositories.restaurant_repo import RestaurantRepository
from src.backend.routers.orders import get_controller
from src.backend.routers.restaurants import get_controller as get_restaurant_controller
from src.backend.repositories.order_repo import OrderRepository
from src.backend.controllers.order_controller import OrderController
from src.backend.repositories.notification_repo import NotificationRepository
from src.backend.controllers.notification_controller import NotificationController
from src.backend.repositories.user_repo import UserRepository
from src.backend.controllers.restaurant_controller import RestaurantController
import src.backend.utils.auth_dependencies as auth_dependencies


@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real data/order.json.
    The temporary file is automatically removed after each test, ensuring the production database is never touched.
    """
    temp_db = tmp_path / "test.json"
    temp_db.write_text(json.dumps([]))

    temp_notif_db = tmp_path / "test_notifications.json"
    temp_notif_db.write_text(json.dumps([]))

    temp_restaurants = tmp_path / "test_restaurants.json"
    temp_restaurants.write_text(json.dumps([]))

    temp_user_db = tmp_path / "test_users.json"
    temp_user_db.write_text(json.dumps({
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
            },
            {
                "id": 3,
                "username": "TestCustomer2",
                "email": "testcustomer2@123.com",
                "password": "Test@123",
                "role": "customer",
                "is_logged_in": False,
                "is_blocked": False
            },
            {
                "id": 4,
                "username": "TestOwner2",
                "email": "testowner2@123.com",
                "password": "Test@123",
                "role": "restaurant owner",
                "is_logged_in": False,
                "is_blocked": False
            },
            {
                "id": 5,
                "username": "TestAdmin",
                "email": "testadmin@123.com",
                "password": "Test@123",
                "role": "administrator",
                "is_logged_in": False,
                "is_blocked": False
            }

        ]
    }))

    resturant_repo = RestaurantRepository(file_path=str(temp_restaurants))
    restaurant_controller = RestaurantController(repo=resturant_repo)

    test_repo = OrderRepository(file_path=str(temp_db))
    test_notif_repo = NotificationRepository(file_path=str(temp_notif_db))
    test_user_repo = UserRepository(file=str(temp_user_db))

    test_notif_controller = NotificationController(repo=test_notif_repo)
    test_controller = OrderController(repo=test_repo, notif_controller=test_notif_controller)

    app.dependency_overrides[get_controller] = lambda: test_controller
    app.dependency_overrides[get_restaurant_controller] = lambda: restaurant_controller
    
    original_repo = auth_dependencies.repo
    auth_dependencies.repo = test_user_repo
    
    client = TestClient(app)
    client.headers.update({"X-User-Id": "1"}) 

    yield client

    auth_dependencies.repo = original_repo
    app.dependency_overrides.clear()

def pytest_sessionfinish():
    '''
    The file data/weekly_offers.json should be cleaned so that it contains no elements after all tests have finished.
    '''
    with open("data/weekly_offers.json", "w") as file:
        file.write("[]")