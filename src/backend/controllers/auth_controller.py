from typing import Optional
import json

from fastapi import HTTPException
from src.backend.models.user import UserBase
from src.backend.repositories.user_repo import UserRepository


class AuthController:
    def __init__(self, repo: Optional[UserRepository] = None) -> None:
        self.repo = repo or UserRepository()

    def register(self, username, email, password, role):
        #TODO -- after SaveUser function is complete inside the user repository, finish this register user function
        pass
        
    def login(self, email, password):
        userInfo = self.repo.get_user_by_email(email)
        if userInfo == None:
            raise HTTPException(status_code=404, detail="User not found")
        if password == userInfo['password']:
              return userInfo
        else:
            raise HTTPException(status_code=400, detail="Password is incorrect")

