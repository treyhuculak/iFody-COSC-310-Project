from src.backend.models.order import OrderCreate
from src.backend.services.admin_service import AdminService
import pytest, typing

admin_service = None

@pytest.fixture
def setup_admin_service() -> None:
    '''
    Initializes variable admin_service using the __init__ function of the AdminService class.
    '''
    global admin_service
    admin_service = AdminService()

@pytest.fixture
def setup_admin_service_with_draft_order_db() -> typing.Generator:
    '''
    Initializes variable admin_service and sets up a draft database for orders.
    '''
    global admin_service
    admin_service = AdminService("data/draft_order_db.json")
    yield
    import os
    os.remove(os.getcwd() + "/data/draft_order_db.json")

def test_empty_get_all_orders(setup_admin_service) -> None:
    '''
    Tests the get_all_orders function when there are no orders in the database.
    '''
    assert admin_service.get_all_orders() == []

def test_empty_get_most_popular_restaurant(setup_admin_service) -> None:
    '''
    Tests the get_most_popular_restaurant function when there are no orders in the database.
    '''
    assert admin_service.get_most_popular_restaurant() == None

def test_nonempty_get_all_orders(setup_admin_service_with_draft_order_db) -> None:
    '''
    Tests the get_all_orders function before and after creating orders in the draft database.
    '''
    assert len(admin_service.get_all_orders()) == 0
    admin_service.order_repo.create_order(
        {
            "customer_id": 1,
            "restaurant_id": 1,
            "status": "pending",
            "location": "BC",
            "order_items": []
        }
    )
    assert len(admin_service.get_all_orders()) == 1
    admin_service.order_repo.create_order(
        {
            "customer_id": 2,
            "restaurant_id": 2,
            "status": "pending",
            "location": "BC",
            "order_items": []
        }
    )
    assert len(admin_service.get_all_orders()) == 2

def test_nonempty_get_most_popular_restaurant(setup_admin_service_with_draft_order_db) -> None:
    admin_service.order_repo.create_order(
        {
            "customer_id": 1,
            "restaurant_id": 1,
            "status": "pending",
            "location": "BC",
            "order_items": []
        }
    )
    assert admin_service.get_most_popular_restaurant() != None
    assert admin_service.get_most_popular_restaurant()["id"] == 1
    admin_service.order_repo.create_order(
        {
            "customer_id": 2,
            "restaurant_id": 2,
            "status": "pending",
            "location": "BC",
            "order_items": []
        }
    )
    admin_service.order_repo.create_order(
        {
            "customer_id": 3,
            "restaurant_id": 2,
            "status": "pending",
            "location": "BC",
            "order_items": []
        }
    )
    assert admin_service.get_most_popular_restaurant()["id"] == 2
    admin_service.order_repo.create_order(
        {
            "customer_id": 4,
            "restaurant_id": 1,
            "status": "pending",
            "location": "BC",
            "order_items": []
        }
    )
    assert admin_service.get_most_popular_restaurant()["id"] == 1