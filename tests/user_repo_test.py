from src.backend.repositories.user_repo import UserRepository
import pytest

repo = UserRepository()
user_example = {
    "id": 1,
    "username": "TestCustomer",
    "email": "testcustomer@123.com",
    "password": "Test@123",
    "role": "Customer",
    "is_logged_in": False,
    "is_blocked": False
}

@pytest.fixture
def setup_user_db() -> None:
    '''
    Makes sure there is only one instance in the database before each test function runs.
    '''
    repo._reinit_database()
    repo.add_user(user_example)

def test_add_user_with_correct_id_value(setup_user_db) -> None:
    '''
    Tests the add_user function and makes sure the value of id is correct.
    '''
    user_example_2 = {
        "id": 1,
        "username": "TestCustomerNum2",
        "email": "testcustomernum2@123.com",
        "password": "Test@12345",
        "role": "Customer",
        "is_logged_in": False,
        "is_blocked": False
    }
    repo.add_user(user_example_2)
    assert user_example_2["id"] == 2
    assert len(repo.get_all_users()) == 2

def test_get_all_users(setup_user_db) -> None:
    '''
    Tests the get_all_users function.
    '''
    assert repo.get_all_users() != None
    assert repo.get_all_users() == [user_example]

def test_valid_get_user_by_id(setup_user_db) -> None:
    '''
    Tests valid input for the get_user_by_id function.
    '''
    assert repo.get_user_by_id(1) != None
    assert repo.get_user_by_id(1) == user_example

def test_invalid_get_user_by_id(setup_user_db) -> None:
    '''
    Tests invalid input for the get_user_by_id function.
    '''
    assert repo.get_user_by_id(0) == None
    assert repo.get_user_by_id(-1) == None

def test_valid_get_user_by_username(setup_user_db) -> None:
    '''
    Tests valid input for the get_user_by_username function.
    '''
    assert repo.get_user_by_username("TestCustomer") != None
    assert repo.get_user_by_username("TestCustomer") == user_example
    
def test_invalid_get_user_by_username(setup_user_db) -> None:
    '''
    Tests invalid input for the get_user_by_username function.
    '''
    assert repo.get_user_by_username("FakeCustomer") == None

def test_valid_get_user_by_email(setup_user_db) -> None:
    '''
    Tests valid input for the get_user_by_email function.
    '''
    assert repo.get_user_by_email("testcustomer@123.com") != None
    assert repo.get_user_by_email("testcustomer@123.com") == user_example

def test_invalid_get_user_by_email(setup_user_db) -> None:
    '''
    Tests invalid input for the get_user_by_email function.
    '''
    assert repo.get_user_by_email("fakecustomer@123.com") == None