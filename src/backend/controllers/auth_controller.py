from typing import Optional

from fastapi import HTTPException
from src.backend.repositories.user_repo import UserRepository


class AuthController:
    def __init__(self, repo: Optional[UserRepository] = None) -> None:
        self.repo = repo or UserRepository()

    def register(self, username: str, email: str, password: str, role: str):
        pass
        
    def login(self, email: str, password: str):
        user_info = self.repo.get_user_by_email(email)
        if user_info == None:
            raise HTTPException(status_code = 404, detail = "The account is not found.")
        if password == user_info['password']:
              return user_info
        else:
            raise HTTPException(status_code = 400, detail = "The password is incorrect.")