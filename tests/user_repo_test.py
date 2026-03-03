from src.backend.repositories.user_repo import UserRepository

repo = UserRepository()

def test_get_all_users() -> None:
    '''
    Tests the get_all_users function.
    '''
    assert(repo.get_all_users() != None)

def test_valid_get_user_by_username() -> None:
    '''
    Tests valid input for the get_user_by_username function.
    '''
    assert (repo.get_user_by_username("TestCustomer") != None)
    
def test_invalid_get_user_by_username() -> None:
    '''
    Tests invalid input for the get_user_by_username function.
    '''
    assert (repo.get_user_by_username("FakeCustomer") == None)

def test_valid_get_user_by_email() -> None:
    '''
    Tests valid input for the get_user_by_email function.
    '''
    assert(repo.get_user_by_email("testcustomer@123.com") != None)

def test_invalid_get_user_by_email() -> None:
    '''
    Tests invalid input for the get_user_by_email function.
    '''
    assert(repo.get_user_by_email("fakecustomer@123.com") == None)