from typing import Optional

from fastapi import HTTPException
from src.backend.models.user import UserSave, Role
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

    def register(self, username: str, email: str, password: str, role: Role):
        '''
        Creates an account instance and saves it to the database when the email, password, and role are all valid.
        '''
        users = self.repo.get_all_users()
        usernames = [user["username"] for user in users]
        emails = [user["email"] for user in users]
        if (username in usernames) or (email in emails):
            raise AccountExistsException("The account already exists. Try logging in to the account.")
        new_user = UserSave(id = 1, username = username, email = email, password = password, role = role)
        user_dict = new_user.model_dump()
        
        if hasattr(user_dict['role'], 'value'): #If role gets converted to Enum by Pydantic, convert back to string
            user_dict['role'] = user_dict['role'].value

        self.repo.add_user(user_dict)
        
    def login(self, email: str, password: str):
        '''
        Logs in using the email and password given.
        '''
        user_info = self.repo.get_user_by_email(email)

        if user_info == None:
            raise HTTPException(status_code = 404, detail = "The account is not found.")
        if password == user_info['password']:
              user_info["is_logged_in"] = True
              return user_info
        else:
            raise HTTPException(status_code = 400, detail = "The password is incorrect.")