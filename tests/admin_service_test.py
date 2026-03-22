from src.backend.services.admin_service import AdminService
import pytest, typing

admin_service = None

@pytest.fixture
def setup_admin_service_with_temp_db() -> typing.Generator:
    '''
    Initializes variable admin_service and sets up a draft database for orders.
    '''
    global admin_service
    admin_service = AdminService("data/draft_order_db.json", "data/draft_user_db.json")
    yield
    import os
    os.remove(os.getcwd() + "/data/draft_order_db.json")
    os.remove(os.getcwd() + "/data/draft_user_db.json")

def test_delete_user_with_invalid_username(setup_admin_service_with_temp_db) -> None:
    '''
    Tests the delete_user function by calling it with invalid usernames.
    '''
    assert admin_service.delete_user("") == None
    assert admin_service.delete_user("FakeUsername") == None

def test_delete_user_with_valid_username(setup_admin_service_with_temp_db) -> None:
    '''
    Tests the delete_user function by calling it with a valid username.
    '''
    user_example = {
        "id": 1,
        "username": "TestCustomer",
        "email": "testcustomer@123.com",
        "password": "Test@123",
        "role": "Customer",
        "is_logged_in": False,
        "is_blocked": False
    }
    admin_service.user_repo.add_user(user_example)
    assert admin_service.delete_user('TestCustomer') == user_example

def test_block_user_with_invalid_username(setup_admin_service_with_temp_db) -> None:
    '''
    Tests the block_user function by calling it with invalid usernames.
    '''
    assert admin_service.block_user("") == None
    assert admin_service.block_user("FakeUsername") == None

def test_block_user_with_valid_username(setup_admin_service_with_temp_db) -> None:
    '''
    Tests the block_user function by calling it with a valid username.
    '''
    user_example = {
        "id": 1,
        "username": "TestCustomer",
        "email": "testcustomer@123.com",
        "password": "Test@123",
        "role": "Customer",
        "is_logged_in": False,
        "is_blocked": False
    }
    admin_service.user_repo.add_user(user_example)
    blocked = admin_service.block_user(user_example["username"])
    assert blocked != None
    assert blocked == {
        "id": 1,
        "username": "TestCustomer",
        "email": "testcustomer@123.com",
        "password": "Test@123",
        "role": "Customer",
        "is_logged_in": False,
        "is_blocked": True
    }

def test_unblock_user_with_invalid_username(setup_admin_service_with_temp_db) -> None:
    '''
    Tests the unblock_user function by calling it with invalid usernames.
    '''
    user_example = {
        "id": 1,
        "username": "TestCustomer",
        "email": "testcustomer@123.com",
        "password": "Test@123",
        "role": "Customer",
        "is_logged_in": False,
        "is_blocked": False
    }
    admin_service.user_repo.add_user(user_example)
    admin_service.block_user(user_example["username"])
    assert admin_service.block_user("") == None
    assert admin_service.block_user("FakeUsername") == None
    assert admin_service.user_repo.get_user_by_username(user_example["username"])["is_blocked"]

def test_unblock_user_with_valid_username(setup_admin_service_with_temp_db) -> None:
    '''
    Tests the unblock_user function by calling it with a valid username.
    '''
    user_example = {
        "id": 1,
        "username": "TestCustomer",
        "email": "testcustomer@123.com",
        "password": "Test@123",
        "role": "Customer",
        "is_logged_in": False,
        "is_blocked": False
    }
    admin_service.user_repo.add_user(user_example)
    admin_service.block_user(user_example["username"])
    unblocked = admin_service.unblock_user(user_example["username"])
    assert not unblocked["is_blocked"]
    assert not admin_service.user_repo.get_user_by_username(user_example["username"])["is_blocked"]

def test_empty_get_all_orders(setup_admin_service_with_temp_db) -> None:
    '''
    Tests the get_all_orders function when there are no orders in the database.
    '''
    assert admin_service.get_all_orders() == []

def test_empty_get_most_popular_restaurant(setup_admin_service_with_temp_db) -> None:
    '''
    Tests the get_most_popular_restaurant function when there are no orders in the database.
    '''
    assert admin_service.get_most_popular_restaurant() == None

def test_nonempty_get_all_orders(setup_admin_service_with_temp_db) -> None:
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

def test_nonempty_get_most_popular_restaurant(setup_admin_service_with_temp_db) -> None:
    '''
    Tests the get_most_popular_restaurant function after creating orders in the draft database.
    It also tests the case where there are multiple restaurants with the same number of orders.
    '''
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

def test_get_average_delivery_time(setup_admin_service_with_temp_db) -> None:
    '''
    Tests the get_average_delivery_time function by checking if the average delivery time is between 10 and 60 minutes.
    '''
    average_delivery_time = admin_service.get_average_delivery_time()
    assert average_delivery_time >= 10
    assert average_delivery_time <= 60

def test_get_gross_revenue_by_restaurant_id(setup_admin_service_with_temp_db) -> None:
    '''
    Tests the get_gross_revenue_by_restaurant_id function with different orders.
    '''
    admin_service.order_repo.create_order(
        {
            "customer_id": 1,
            "restaurant_id": 1,
            "status": "pending",
            "location": "BC",
            "order_items": []
        }
    )
    assert admin_service.get_gross_revenue_by_restaurant_id(1) == 0
    admin_service.order_repo.create_order(
        {
            "customer_id": 2,
            "restaurant_id": 1,
            "status": "pending",
            "location": "BC",
            "order_items": [
                {"item_id": 101, "quantity": 2, "price_at_purchase": 5.0}
            ]
        }
    )
    wished_revenue = float('%.1f' % (5 * 2 * (1 + 0.12)))
    assert admin_service.get_gross_revenue_by_restaurant_id(1) == wished_revenue