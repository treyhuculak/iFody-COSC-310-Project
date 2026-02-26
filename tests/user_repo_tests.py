import pytest

from src.backend.repositories.user_repo import UserRepository

repo = UserRepository()

def test_valid_getUserByUsername() -> None:
    '''
    Testing valid input for function getUserByUsername()
    '''
    assert (repo.getUserByUsername("TestUser") != None)
    
def test_invalid_getUserByUsername() -> None:
    '''
    Testing invalid input for function getUserByUsername()
    '''
    assert (repo.getUserByUsername("FakeUser") == None)

def test_valid_getUserByEmail() -> None:
    '''
    Testing valid input for function getUserByEmail()
    '''
    assert(repo.getUserByEmail("testuser@email.com") != None)

def test_invalid_getUserByEmail() -> None:
    '''
    Testing invalid input for function getUserByEmail()
    '''
    assert(repo.getUserByEmail("fakeuser@email.com") == None)


