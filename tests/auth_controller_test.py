import pytest
from fastapi import HTTPException
from src.backend.controllers.auth_controller import AuthController
from src.backend.repositories.user_repo import UserRepository

repo = UserRepository
controller = AuthController()

def test_valid_login() -> None:
    assert (controller.login("testcustomer@123.com", "Test@123") != None)

def test_invalid_login() -> None:
    with pytest.raises(HTTPException):
        controller.login("fakeuser@111.com", "fakePassword")

def test_validemail_invalidpass() -> None:
    with pytest.raises(HTTPException):
        controller.login("testcustomer@123.com", "fakePassword")