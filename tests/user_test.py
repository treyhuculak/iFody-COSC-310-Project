import pytest
from src.backend.models import user

def test_user_with_valid_email() -> None:
    '''
    Tests the User class constructor with a valid email address.
    '''
    user = user.User('TempUser', 'tempuser@tu.com', '1234', 'customer', False)
    assert user == "User('TempUser', 'tempuser@tu.com', '1234', 'customer', False)"

def test_user_with_invalid_email() -> None:
    '''
    Tests the User class constructor with an invalid email address.
    '''
    with pytest.raises(ValueError):
        user = user.User('TempUser', '', '1234', 'customer', False)