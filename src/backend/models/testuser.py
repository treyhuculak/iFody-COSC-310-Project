from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str
    password: str

class UserCreate(UserBase):
    username: Field(..., min_length=3)  # Username must be at least 3 characters long
    email: str
    password: Field(..., min_length=6)  # Password must be at least 6 characters long

class User(UserBase):
    id: int
    role: str
    is_blocked: bool