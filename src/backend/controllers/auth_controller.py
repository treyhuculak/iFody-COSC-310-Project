from typing import Optional

from fastapi import HTTPException
from src.backend.models.user import UserSave
from src.backend.repositories.user_repo import UserRepository

class AccountExistsException(Exception):
    """
    Raise it when the account is already in the database for the register function.
    """
    pass

class NotLoggedInException(Exception):
    '''
    Raise it when the user attempts to log out but no account is logged in.
    '''
    pass

class AuthController:
    def __init__(self, repo: Optional[UserRepository] = None) -> None:
        '''
        Initializes the AuthController class with the necessary fields.
        A self.cur_user variable is added to keep track of the potentially logged-in user account.
        '''
        self.repo = repo or UserRepository()
        self.cur_user = None

    def register(self, username: str, email: str, password: str, role: str):
        '''
        Creates an account instance and saves it to the database when the email, password, and role are all valid.
        '''
        users = self.repo.get_all_users()
        usernames = [user["username"] for user in users]
        emails = [user["email"] for user in users]
        if (username in usernames) or (email in emails):
            raise AccountExistsException("The account already exists. Try logging in to the account.")
        new_user = UserSave(id = 1, username = username, email = email, password = password, role = role)
        new_user = new_user.model_dump()
        self.repo.add_user(new_user)
        
    def login(self, email: str, password: str):
        '''
        Logs in using the email and password given.
        '''
        user_info = self.repo.get_user_by_email(email)
        if user_info == None:
            raise HTTPException(status_code = 404, detail = "The account is not found.")
        if password == user_info['password']:
            user_info["is_logged_in"] = True
            self.cur_user = user_info
            return self.cur_user
        else:
            raise HTTPException(status_code = 400, detail = "The password is incorrect.")
        
    def logout(self) -> None:
        '''
        Logs out the user and updates the is_logged_in field in the dictionary.
        '''
        if self.cur_user:
            self.cur_user["is_logged_in"] = False
            self.cur_user = None
        else:
            raise NotLoggedInException("Please sign in to the account first.")