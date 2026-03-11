import pytest, typing
from fastapi import HTTPException
from src.backend.controllers.auth_controller import AuthController, AccountExistsException
from src.backend.repositories.user_repo import UserRepository
from src.backend.models.user import InvalidEmailError, InvalidPasswordError, Role

controller = AuthController()
controller.repo = UserRepository("data/temp_user_db.json")
user_example = {
    "id": 1,
    "username": "TestCustomer",
    "email": "testcustomer@123.com",
    "password": "Test@123",
    "role": Role.CUSTOMER.value,
    "is_logged_in": False,
    "is_blocked": False
}

@pytest.fixture
def setup_database() -> typing.Generator:
    '''
    Makes sure there is only one instance in the database before each test function runs.
    '''
    controller.repo._reinit_database()
    controller.repo.add_user(user_example)
    yield
    import os
    os.remove(os.getcwd() + "/data/temp_user_db.json")

def test_valid_register(setup_database) -> None:
    '''
    Tests the register functionality using a valid email format, a valid password format, and a valid value for role.
    '''
    controller.register("TestCustomerV2", "tcv2@outlook.com", "Abc@5678", Role.CUSTOMER.value)

def test_invalid_email_register(setup_database) -> None:
    '''
    Tests the register functionality using an invalid email format.
    '''
    with pytest.raises(InvalidEmailError):
        controller.register("TestCustomerV2", "NotEvenAnEmailAddress", "Abc@5678", Role.CUSTOMER)

def test_invalid_password_register(setup_database) -> None:
    '''
    Tests the register functionality using an invalid password format.
    '''
    with pytest.raises(InvalidPasswordError):
        controller.register("TestCustomerV2", "tcv2@outlook.com", "NotValid", Role.CUSTOMER.value)

def test_invalid_role_register(setup_database) -> None:
    '''
    Tests the register functionality using an invalid role value.
    '''
    with pytest.raises(Exception):
        controller.register("TestCustomerV2", "tcv2@outlook.com", "Abc@5678", "CoolDude")

def test_register_with_existing_account(setup_database) -> None:
    '''
    Tests the register functionality using an existing account.
    '''
    with pytest.raises(AccountExistsException):
        controller.register("TestCustomer", "testcustomer@123.com", "Test@123", Role.CUSTOMER.value)

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
        "role": Role.CUSTOMER.value,
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