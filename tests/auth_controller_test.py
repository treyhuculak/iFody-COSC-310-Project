import pytest
from fastapi import HTTPException
from src.backend.controllers.auth_controller import AuthController
from src.backend.repositories.user_repo import UserRepository

controller = AuthController()

def test_valid_login() -> None:
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

def test_invalid_login() -> None:
    '''
    Tests the login function with a nonexistent email and an incorrect password.
    '''
    with pytest.raises(HTTPException):
        controller.login("fakeuser@111.com", "fakePassword")

def test_login_invalid_password() -> None:
    '''
    Tests the login functionality using a valid email with an incorrect password.
    '''
    with pytest.raises(HTTPException):
        controller.login("testcustomer@123.com", "fakePassword")