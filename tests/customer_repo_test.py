import pytest

from src.backend.repositories.user_repo import CustomerRepository

repo = CustomerRepository()

def test_get_all_customers() -> None:
    '''
    Testing the function get_all_customers()
    '''
    assert(repo.get_all_customers() != None)

def test_valid_get_customer_by_username() -> None:
    '''
    Testing valid input for function get_customer_by_username()
    '''
    assert (repo.get_customer_by_username("TestCustomer") != None)
    
def test_invalid_get_customer_by_username() -> None:
    '''
    Testing invalid input for function get_customer_by_username()
    '''
    assert (repo.get_customer_by_username("FakeCustomer") == None)

def test_valid_get_customer_by_email() -> None:
    '''
    Testing valid input for function get_customer_by_email()
    '''
    assert(repo.get_customer_by_email("testcustomer@123.com") != None)

def test_invalid_get_customer_by_email() -> None:
    '''
    Testing invalid input for function get_customer_by_email()
    '''
    assert(repo.get_customer_by_email("fakecustomer@123.com") == None)


