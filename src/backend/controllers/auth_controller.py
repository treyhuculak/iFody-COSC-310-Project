from typing import Union

from fastapi import HTTPException
from src.backend.models.user import Admin, Customer, RestaurantOwner
from src.backend.repositories.user_repo import UserRepository