import pytest, pydantic_core
from src.backend.models.user import UserSave, InvalidEmailError, InvalidPasswordError, Role

'''
Since the Admin, Customer, and RestaurantOwner instances all inherit from User and differ only in their role, we only need to test one of them to verify the behavior.
'''

def test_customer_with_valid_email() -> None:
    '''
    Tests the Customer instance when attempting to log in with a valid email address.
    '''
    customer = UserSave(id = 1, username = 'TempUser', email = 'tempuser@tu.com', password = 'Abc@1234', role = Role.CUSTOMER)

def test_customer_with_invalid_email() -> None:
    '''
    Tests the Customer instance when attempting to log in with an invalid email address.
    '''
    with pytest.raises(pydantic_core.ValidationError):
        customer = UserSave(id = 1, username = 'TempUser', email = '', password = 'Abc@1234', role = Role.CUSTOMER)

    with pytest.raises(InvalidEmailError):
        customer = UserSave(id = 1, username = 'TempUser', email = 'RandomString', password = 'OhYeah', role = Role.CUSTOMER)

def test_customer_with_valid_password() -> None:
    '''
    Tests the Customer instance when attempting to log in with a valid password.
    '''
    customer = UserSave(id = 1, username = 'TempUser', email = 'tempuser@tu.com', password = 'Abc@1234', role = Role.CUSTOMER)

def test_customer_with_invalid_password() -> None:
    '''
    Tests the Customer instance when attempting to log in with an invalid password.
    '''
    with pytest.raises(pydantic_core.ValidationError):
        customer = UserSave(id = 1, username = 'TempUser', email = 'tempuser@tu.com', password = '', role = Role.CUSTOMER)

    with pytest.raises(InvalidPasswordError):
        customer = UserSave(id = 1, username = 'TempUser', email = 'tempuser@tu.com', password = '1234', role = Role.CUSTOMER)