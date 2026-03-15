from src.backend.services.admin_service import AdminService
import pytest, typing

admin_service = None

@pytest.fixture
def setup_database() -> typing.Generator:
    '''
    Makes sure the draft databases are correctly created before tests run and deleted afterward.
    '''
    global admin_service
    admin_service = AdminService("data/temp_rest_db.json", "data/temp_order_db.json")
    yield
    import os
    os.remove(os.getcwd() + "/data/temp_rest_db.json")
    os.remove(os.getcwd() + "/data/temp_order_db.json")

def test_empty_get_all_orders(setup_database) -> None:
    assert admin_service.get_all_orders() == []

def test_empty_get_most_popular_restaurant(setup_database) -> None:
    assert admin_service.get_most_popular_restaurant() == None