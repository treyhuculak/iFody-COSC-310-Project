from fastapi.testclient import TestClient
import json, pytest
from src.backend.controllers.auth_controller import AuthController
from src.backend.controllers.notification_controller import NotificationController
from src.backend.main import app
from src.backend.repositories.user_repo import UserRepository
from src.backend.repositories.notification_repo import NotificationRepository
from src.backend.routers.auth import get_controller
from src.backend.services.admin_service import AdminService
from src.backend.utils import auth_dependencies

@pytest.fixture
def test_client(tmp_path):
    """
    Provides a TestClient backed by a temporary JSON file instead of the real database.
    The temporary file is automatically deleted after each test so the production database is never touched.
    """
    temp_user_database = tmp_path / "temp_user_database.json"
    temp_user_database.write_text(json.dumps({
                "Users": [
                    {
                        "id": 1,
                        "username": "DraftAdministrator",
                        "email": "DraftAdministrator@123.com",
                        "password": "Drad@246",
                        "role": "administrator", 
                        "is_logged_in": False,
                        "is_blocked": False
                    },
                    {
                        "id": 2,
                        "username": "TestCustomer",
                        "email": "TestCustomer@123.com",
                        "password": "Tecu@248",
                        "role": "customer", 
                        "is_logged_in": False,
                        "is_blocked": False
                    },
                    {
                        "id": 3,
                        "username": "DraftRestaurantOwner",
                        "email": "DraftRestaurantOwner@123.com",
                        "password": "Tecu@248",
                        "role": "restaurant owner", 
                        "is_logged_in": False,
                        "is_blocked": False
                    }
                ]
            }
        )
    )

    test_order_database = tmp_path / "test_order_database.json"
    test_order_database.write_text(json.dumps(
            [
                {
                    "customer_id": 1,
                    "restaurant_id": 1,
                    "status": "pending",
                    "location": "BC",
                    "order_items": []
                },
                {
                    "customer_id": 2,
                    "restaurant_id": 2,
                    "status": "pending",
                    "location": "BC",
                    "order_items": []
                },
                {
                    "customer_id": 3,
                    "restaurant_id": 1,
                    "status": "pending",
                    "location": "BC",
                    "order_items": [
                        {
                            "item_id": 101,
                            "quantity": 2,
                            "price_at_purchase": 5.0
                        }
                    ]
                },
                {
                    "customer_id": 4,
                    "restaurant_id": 2,
                    "status": "pending",
                    "location": "BC",
                    "order_items": [
                        {
                            "item_id": 101,
                            "quantity": 8,
                            "price_at_purchase": 2.5
                        }
                    ]
                }
            ]
        )
    )
    temp_notif_database = tmp_path / "temp_notif_db.json"
    temp_notif_database.write_text(json.dumps([]))

    test_user_repo = UserRepository(str(temp_user_database))
    test_notif_repo = NotificationRepository(str(temp_notif_database))
    test_notif_controller = NotificationController(repo=test_notif_repo)
    test_admin_service = AdminService(str(test_order_database), str(temp_user_database))
    test_controller = AuthController(test_user_repo, test_admin_service, test_notif_controller)

    app.dependency_overrides[get_controller] = lambda: test_controller
    original_repo = auth_dependencies.repo
    auth_dependencies.repo = test_user_repo
    
    client = TestClient(app)
    client.headers.update({"X-User-Id": "1"}) 

    yield client
    auth_dependencies.repo = original_repo
    app.dependency_overrides.clear()

def test_block_user_valid_username(test_client):
    '''
    Tests the block_user function using a valid username.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftAdministrator@123.com",
            "password": "Drad@246"
        }
    )
    response = test_client.post("/auth/blocked/%s" % "TestCustomer")
    assert response.status_code == 200
    assert response.json() != None
    assert response.json()["is_blocked"]

def test_block_user_invalid_username(test_client):
    '''
    Tests the block_user function using invalid usernames.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftAdministrator@123.com",
            "password": "Drad@246"
        }
    )
    response = test_client.post("/auth/blocked/%s" % "1234")
    assert response.status_code == 200
    assert response.json() == None
    response = test_client.post("/auth/blocked/%s" % "")
    assert response.status_code == 404
    assert "Not Found" in response.json().values()

def test_unblock_user_valid_username(test_client):
    '''
    Tests the unblock_user function using a valid username.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftAdministrator@123.com",
            "password": "Drad@246"
        }
    )
    test_client.post("/auth/blocked/%s" % "TestCustomer")
    response = test_client.delete("/auth/blocked/%s" % "TestCustomer")
    assert response.status_code == 200
    assert response.json() != None
    assert not response.json()["is_blocked"]

def test_unblock_user_invalid_username(test_client):
    '''
    Tests the unblock_user function using invalid usernames.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftAdministrator@123.com",
            "password": "Drad@246"
        }
    )
    test_client.post("/auth/blocked/%s" % "TestCustomer")
    response = test_client.delete("/auth/blocked/%s" % "1234")
    assert response.status_code == 200
    assert response.json() == None
    response = test_client.delete("/auth/blocked/%s" % "")
    assert response.status_code == 404
    assert "Not Found" in response.json().values()

def test_delete_user_valid_username(test_client):
    '''
    Tests the delete_user function using a valid username.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftAdministrator@123.com",
            "password": "Drad@246"
        }
    )
    response = test_client.delete("/auth/register/%s" % "TestCustomer")
    assert response.status_code == 200
    assert response.json() != None
    assert response.json() == {
        "id": 2,
        "username": "TestCustomer",
        "email": "TestCustomer@123.com",
        "password": "Tecu@248",
        "role": "customer", 
        "is_logged_in": False,
        "is_blocked": False
    }

def test_delete_user_invalid_username(test_client):
    '''
    Tests the delete_user function using invalid usernames.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftAdministrator@123.com",
            "password": "Drad@246"
        }
    )
    response = test_client.delete("/auth/register/%s" % "")
    assert response.status_code == 405
    assert "Method Not Allowed" in response.json().values()
    response = test_client.delete("/auth/register/%s" % "1234")
    assert response.status_code == 200
    assert response.json() == None

def test_get_all_orders(test_client):
    '''
    Tests the get_all_orders function by letting an administrator call it.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftAdministrator@123.com",
            "password": "Drad@246"
        }
    )
    response = test_client.get("/auth/statistics/order")
    assert response.status_code == 200
    assert response.json() != None
    assert response.json() == [
        {
            "customer_id": 1,
            "restaurant_id": 1,
            "status": "pending",
            "location": "BC",
            "order_items": []
        },
        {
            "customer_id": 2,
            "restaurant_id": 2,
            "status": "pending",
            "location": "BC",
            "order_items": []
        },
        {
            "customer_id": 3,
            "restaurant_id": 1,
            "status": "pending",
            "location": "BC",
            "order_items": [
                {
                    "item_id": 101,
                    "quantity": 2,
                    "price_at_purchase": 5.0
                }
            ]
        },
        {
            "customer_id": 4,
            "restaurant_id": 2,
            "status": "pending",
            "location": "BC",
            "order_items": [
                {
                    "item_id": 101,
                    "quantity": 8,
                    "price_at_purchase": 2.5
                }
            ]
        }
    ]

def test_get_all_orders_by_restaurant_owner(test_client):
    '''
    Tests the get_all_orders function by letting a restaurant owner call it.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftRestaurantOwner@123.com",
            "password": "Tecu@248"
        }
    )
    response = test_client.get("/auth/statistics/order")
    assert response.status_code == 403
    assert response.json() != None
    assert "Only administrators can access all the orders." in response.json().values()

def test_get_gross_revenue_by_restaurant_id(test_client):
    '''
    Tests the get_gross_revenue_by_restaurant_id function by letting an administrator call it.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftAdministrator@123.com",
            "password": "Drad@246"
        }
    )
    response = test_client.get("/auth/statistics/gross_revenue/%d" % 1)
    assert response.status_code == 200
    assert response.json() != None
    matched_revenue = 11.2
    assert response.json() == matched_revenue
    response = test_client.get("/auth/statistics/gross_revenue/%d" % 2)
    assert response.status_code == 200
    assert response.json() != None
    matched_revenue = 22.4
    assert response.json() == matched_revenue

def test_get_gross_revenue_by_restaurant_id_restaurant_owner(test_client):
    '''
    Tests the get_gross_revenue_by_restaurant_id function by letting a restaurant owner call it.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftRestaurantOwner@123.com",
            "password": "Tecu@248"
        }
    )
    response = test_client.get("/auth/statistics/gross_revenue/%d" % 1)
    assert response.status_code == 403
    assert response.json() != None
    assert "Only administrators can check the gross revenue of the restaurant." in response.json().values()
    response = test_client.get("/auth/statistics/gross_revenue/%d" % 2)
    assert response.status_code == 403
    assert response.json() != None
    assert "Only administrators can check the gross revenue of the restaurant." in response.json().values()

def test_get_average_delivery_time(test_client):
    '''
    Tests the get_average_delivery_time function by letting an administrator call it.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftAdministrator@123.com",
            "password": "Drad@246"
        }
    )
    response = test_client.get("/auth/statistics/average_delivery_time")
    assert response.status_code == 200
    assert response.json() != None
    assert 10 <= response.json() <= 60

def test_get_average_delivery_time_restaurant_owner(test_client):
    '''
    Tests the get_average_delivery_time function by letting a restaurant owner call it.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftRestaurantOwner@123.com",
            "password": "Tecu@248"
        }
    )
    response = test_client.get("/auth/statistics/average_delivery_time")
    assert response.status_code == 403
    assert response.json() != None
    assert "Only administrators can check the average delivery time." in response.json().values()

def test_get_most_popular_restaurant(test_client):
    '''
    Tests the get_most_popular_restaurant function by letting an administrator call it.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftAdministrator@123.com",
            "password": "Drad@246"
        }
    )
    response = test_client.get("/auth/statistics/most_popular_restaurant")
    assert response.status_code == 200
    assert response.json() != None
    assert response.json()["id"] == 1

def test_get_most_popular_restaurant_restaurant_owner(test_client):
    '''
    Tests the get_most_popular_restaurant function by letting a restaurant owner call it.
    '''
    test_client.post(
        "/auth/login/",
        json = {
            "email": "DraftRestaurantOwner@123.com",
            "password": "Tecu@248"
        }
    )
    response = test_client.get("/auth/statistics/most_popular_restaurant")
    assert response.status_code == 403
    assert response.json() != None
    assert "Only administrators can check the most popular restaurant." in response.json().values()