import pytest
from fastapi import HTTPException
from src.backend.controllers.auth_controller import AuthController
from src.backend.repositories.user_repo import UserRepository

controller = AuthController()
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
def setup_database() -> None:
    '''
    Makes sure there is only one instance in the database before each test function runs.
    '''
    repo._reinit_database()
    repo.add_user(user_example)

def test_valid_register(setup_database) -> None:
    controller.register("TestCustomerV2", "tcv2@outlook.com", "Abc@5678", "Customer")

def test_valid_login(setup_database) -> None:
    '''
    Tests the login functionality using an existing email with the correct password.
    '''
    assert controller.login("testcustomer@123.com", "Test@123") != None
    assert controller.login("testcustomer@123.com", "Test@123") == {
        "id": 1,
        "username": "TestCustomer",
        "email": "testcustomer@123.com",
        "password": "Test@123",
        "role": "Customer",
        "is_logged_in": False,
        "is_blocked": False
    }

def test_invalid_login(setup_database) -> None:
    '''
    Tests the login function with a nonexistent email and an incorrect password.
    '''
    with pytest.raises(HTTPException):
        controller.login("fakeuser@111.com", "fakePassword")

def test_login_invalid_password(setup_database) -> None:
    '''
    Tests the login functionality using a valid email with an incorrect password.
    '''
    with pytest.raises(HTTPException):
        controller.login("testcustomer@123.com", "fakePassword")