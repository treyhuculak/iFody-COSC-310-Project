import pytest
from src.backend.models.user import Customer

def test_customer_login_with_valid_email() -> None:
    '''
    Tests the Customer class when attempting to log in with a valid email address.
    '''
    customer = Customer('TempUser', 'tempuser@tu.com', 'Abc@1234', False)
    customer.login()

def test_customer_login_with_invalid_email() -> None:
    '''
    Tests the Customer class when attempting to log in with an invalid email address.
    '''
    customer = Customer('TempUser', '', 'Abc@1234', False)
    with pytest.raises(ValueError):
        customer.login()

    customer = Customer('TempUser', '', 'OhYeah', False)
    with pytest.raises(ValueError):
        customer.login()

def test_customer_login_with_valid_password() -> None:
    '''
    Tests the Customer class when attempting to log in with a valid password.
    '''
    customer = Customer('TempUser', 'tempuser@tu.com', 'Abc@1234', False)
    customer.login()

def test_customer_login_with_valid_password() -> None:
    '''
    Tests the Customer class when attempting to log in with an invalid password.
    '''
    customer = Customer('TempUser', 'tempuser@tu.com', '', False)
    with pytest.raises(ValueError):
        customer.login()

    customer = Customer('TempUser', 'tempuser@tu.com', '1234', False)
    with pytest.raises(ValueError):
        customer.login()