from typing import Optional

from fastapi import HTTPException
from src.backend.repositories.user_repo import UserRepository

class AccountExistsException(Exception):
    """
    Raise it when the account is already in the database for the register function.
    """
    pass

class AuthController:
    def __init__(self, repo: Optional[UserRepository] = None) -> None:
        '''
        Initializes the AuthController class with the necessary fields.
        '''
        self.repo = repo or UserRepository()

    def register(self, username: str, email: str, password: str, role: str):
        '''
        Creates an account instance and saves it to the database when the email, password, and role are all valid.
        '''
        pass
        
    def login(self, email: str, password: str):
        '''
        Logs in using the email and password given.
        '''
        user_info = self.repo.get_user_by_email(email)
        if user_info == None:
            raise HTTPException(status_code = 404, detail = "The account is not found.")
        if password == user_info['password']:
              return user_info
        else:
            raise HTTPException(status_code = 400, detail = "The password is incorrect.")