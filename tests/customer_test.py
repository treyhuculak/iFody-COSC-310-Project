import pytest
from src.backend.models.user import Customer

def test_customer_with_valid_email() -> None:
    '''
    Tests the Customer class when attempting to log in with a valid email address.
    '''
    customer = Customer(id = 1, username = 'TempUser', email = 'tempuser@tu.com', password = 'Abc@1234')

def test_customer_with_invalid_email() -> None:
    '''
    Tests the Customer class when attempting to log in with an invalid email address.
    '''
    with pytest.raises(ValueError):
        customer = Customer(id = 1, username = 'TempUser', email = '', password = 'Abc@1234')

    with pytest.raises(ValueError):
        customer = Customer(id = 1, username = 'TempUser', email = '', password = 'OhYeah')

def test_customer_with_valid_password() -> None:
    '''
    Tests the Customer class when attempting to log in with a valid password.
    '''
    customer = Customer(id = 1, username = 'TempUser', email = 'tempuser@tu.com', password = 'Abc@1234')

def test_customer_with_invalid_password() -> None:
    '''
    Tests the Customer class when attempting to log in with an invalid password.
    '''
    with pytest.raises(ValueError):
        customer = Customer(id = 1, username = 'TempUser', email = 'tempuser@tu.com', password = '')

    with pytest.raises(ValueError):
        customer = Customer(id = 1, username = 'TempUser', email = 'tempuser@tu.com', password = '1234')